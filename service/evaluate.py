from typing import List
from schemas import Evaluation, Contest, Problem, ParticipantAnswer
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from db.mysql import MySQLConnection

load_dotenv()

# LLM 모델과 파서 초기화
parser = PydanticOutputParser(pydantic_object=Evaluation)

template = """
다음은 기술 면접 문제와 그에 대한 모범답안, 그리고 응시자의 답변입니다.

문제: {problem}

모범답안: {ai_answer}

응시자의 답변: {participant_answer}

위 답변을 평가하여 다음 형식으로 응답해주세요:
{format_instructions}

평가 기준:
1. 핵심 개념의 이해도 (30점)
2. 설명의 정확성과 명확성 (30점)
3. 전문 용어의 적절한 사용 (20점)
4. 답변의 구조와 논리성 (20점)
"""

# 프롬프트 템플릿 설정
prompt = PromptTemplate(
    template=template,
    input_variables=["problem", "ai_answer", "participant_answer"],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

# LLM 모델 설정
llm = ChatOpenAI(temperature=0.2, model_name="gpt-4o")

# 체인 구성
chain = prompt | llm | parser


async def get_contest_data(contest_id: int) -> Contest:
    print("\n=== 콘테스트 데이터 조회 시작 ===")
    """MySQL에서 콘테스트 데이터 조회"""
    mysql = MySQLConnection()
    
    # 콘테스트 정보 조회
    contest_query = "SELECT id, title FROM contest WHERE id = %s"\
    
    try:
        print(f"콘테스트 조회 쿼리 실행: {contest_query} with ID={contest_id}")
        result = mysql.execute_query(contest_query, (contest_id,))
        print(f"쿼리 결과: {result}")
        
        if not result:
            raise IndexError(f"Contest ID {contest_id}에 대한 결과가 없습니다.")
            
        contest_result = result[0]
        print(f"콘테스트 정보: {contest_result}")
        
    except Exception as e:
        print(f"데이터베이스 조회 중 오류 발생: {str(e)}")
        print(f"오류 타입: {type(e)}")
        raise Exception(f"콘테스트 조회 실패: {str(e)}")
    
    
    # 문제와 답변 정보 조회
    problems_query = """
        SELECT p.id, p.problem, p.ai_answer,
               a.id as answer_id, a.answer, a.rank_score,
               pt.id as participant_id, pt.nickname
        FROM problem p
        LEFT JOIN answer a ON p.id = a.problem_id
        LEFT JOIN participant pt ON a.participant_id = pt.id
        WHERE p.contest_id = %s
    """
    

    try:
        print(f"콘테스트 조회 쿼리 실행: {problems_query} with ID={contest_id}")
        problems_result = mysql.execute_query(problems_query, (contest_id,))
        print(f"쿼리 결과: {problems_result}")
        
        if not result:
            raise IndexError(f"Contest ID {contest_id}에 대한 결과가 없습니다.")
        
    except Exception as e:
        print(f"데이터베이스 조회 중 오류 발생: {str(e)}")
        print(f"오류 타입: {type(e)}")
        raise Exception(f"콘테스트 조회 실패: {str(e)}")
    
    # 데이터 구조화
    problems_dict = {}
    for row in problems_result:
        if row['id'] not in problems_dict:
            problems_dict[row['id']] = {
                'id': row['id'],
                'problem': row['problem'],
                'ai_answer': row['ai_answer'],
                'answers': []
            }
        
        if row['answer_id']:  # 답변이 있는 경우
            problems_dict[row['id']]['answers'].append(
                ParticipantAnswer(
                    participant_id=row['participant_id'],
                    nickname=row['nickname'],
                    answer=row['answer'],
                    rank_score=row['rank_score']
                )
            )
    print("콘테스트 데이터 조회 완료")
    # Contest 객체 생성
    return Contest(
        id=contest_result['id'],
        title=contest_result['title'],
        problems=[Problem(**p) for p in problems_dict.values()]
    )

async def update_rank_score(problem_id: int, participant_id: int, score: int, feedback: str):
    """평가 점수를 DB에 업데이트"""
    mysql = MySQLConnection()
    update_query = """
        UPDATE answer 
        SET rank_score = %s, feedback = %s
        WHERE problem_id = %s AND participant_id = %s
    """
    mysql.execute_query(update_query, (score,feedback, problem_id, participant_id))

async def update_contest_status(contest_id: int):
    """콘테스트 상태를 EVALUATED로 업데이트"""
    mysql = MySQLConnection()
    update_query = """
        UPDATE contest 
        SET submit = 2  # EVALUATED = 2
        WHERE id = %s
    """
    try:
        mysql.execute_query(update_query, (contest_id,))
        print(f"콘테스트 상태 업데이트 완료: Contest ID {contest_id} -> EVALUATED")
    except Exception as e:
        print(f"콘테스트 상태 업데이트 실패: {str(e)}")
        raise e


async def evaluate_answer(problem: str, ai_answer: str, participant_answer: str) -> Evaluation:
    """개별 답변 평가"""
    print("\n=== 답변 평가 시작 ===")
    print(f"문제: {problem}")
    print(f"모범답안: {ai_answer}")
    print(f"참가자 답변: {participant_answer}")
    
    _input = prompt.format(
        problem=problem,
        ai_answer=ai_answer,
        participant_answer=participant_answer
    )
    
    print("\n=== 프롬프트 ===")
    print(_input)

    response = chain.invoke({"problem": problem, 
            "ai_answer": ai_answer, 
            "participant_answer": participant_answer})
    print("\n=== AI 평가 결과 ===")
    print(f"Raw output: {response}")
    
    # # 파싱 시도
    # try:
    #     result = parser.parse(response)
    #     print(f"Parsed result: {result}\n")
    #     return result
    # except Exception as parsing_error:
    #     # 파싱 오류 자세히 출력
    #     print(f"파싱 오류 발생: {str(parsing_error)}")
    #     print(f"파싱 오류 타입: {type(parsing_error)}")
    # print("\n=== AI 평가 결과 ===")
    # print(f"Raw output: {response}")
    
    # result = parser.parse(response)
    # print(f"Parsed result: {result}\n")
    
    return response

async def evaluate_contest_answers(contest_id: int) -> List[Evaluation]:
    print("\n=== 콘테스트 답변 평가 시작 ===")
    """콘테스트의 모든 답변 평가"""
    # 콘테스트 데이터 조회
    contest = await get_contest_data(contest_id)
    evaluations = []
    print("콘테스트 데이터 조회 완료2")
    # 각 문제별로 모든 참가자의 답변 평가
    for problem in contest.problems:
        # 쓰레드로 만들 수 있나???=================
        for participant_answer in problem.answers:
            evaluation = await evaluate_answer(
                problem=problem.problem,
                ai_answer=problem.ai_answer,
                participant_answer=participant_answer.answer
            )
            # 평가 결과 저장
            participant_answer.rank_score = evaluation.score
            evaluations.append({
                'problem_id': problem.id,
                'participant_id': participant_answer.participant_id,
                'evaluation': evaluation
            })
            
            # DB 업데이트
            print(f"DB 업데이트: 문제 ID {problem.id}, 참가자 ID {participant_answer.participant_id}, 점수 {evaluation.score}")
            await update_rank_score(
                problem_id=problem.id,
                participant_id=participant_answer.participant_id,
                score=evaluation.score,
                feedback=evaluation.feedback
            )
    
    # 모든 평가가 완료되면 콘테스트 상태 업데이트
    await update_contest_status(contest_id)
    print(f"콘테스트 {contest_id} 평가 완료")
    
    return evaluations
