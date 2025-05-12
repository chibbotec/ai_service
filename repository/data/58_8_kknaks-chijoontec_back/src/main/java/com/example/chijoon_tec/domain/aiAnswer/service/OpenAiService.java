package com.example.chijoon_tec.domain.aiAnswer.service;

import com.example.chijoon_tec.domain.aiAnswer.dto.AiRequest;
import com.example.chijoon_tec.domain.aiAnswer.dto.AnswerResponse;
import com.example.chijoon_tec.domain.aiAnswer.dto.PrintRequest;
import com.example.chijoon_tec.domain.category.repository.PrimaryRepository;
import com.example.chijoon_tec.domain.category.repository.SecondaryRepository;
import com.example.chijoon_tec.domain.tec.entity.Tec;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.lang.reflect.Field;
import java.util.List;
import java.util.stream.Collectors;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.ai.openai.OpenAiChatModel;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
@Slf4j
public class OpenAiService {

  private final OpenAiChatModel openAiChatModel;
  private final PrimaryRepository primaryRepository;
  private final SecondaryRepository secondaryRepository;

  public String summarizeData(List<PrintRequest> request) {

    List<AiRequest> tecList = request.stream()
        .map(printRequest -> AiRequest.builder()
            .primaryCategory(printRequest.getPrimaryCategory())
            .secondaryCategory(printRequest.getSecondaryCategory())
            .technology(printRequest.getTechnology())
            .description(printRequest.getDescription())
            .jobPosting(printRequest.getJobPosting())
            .sourceURL(printRequest.getSourceURL())
            .build())
        .collect(Collectors.toList());

    StringBuilder prompt = new StringBuilder();
    prompt.append("primaryCategory, secondaryCategory, technology 순으로 묶어서 각"
        + " technology 별로 description을 적어줘\n"
        + " description은 추가하고 여러개일 경우는 []안에 넣어서 응답하고 각 항목에 - 를 붙여서 출력해줘\n"
        + "  jobPosting이랑 sourceURL은 빼줘\n\n");

//    prompt.append(
//        "예시는 다음이 Json형식으로 출력해줘\n"
//            + "primaryCategory필드는 1. Backend 이런식으로 \n "
//            + "secondaryCategory필드는 1) Java 이렇게\n"
//            + "technology필드는 기술스택: 0000000 이렇게\n"
//            + "description필드는 '적용내용: '\n"
//            + "'- Spring은 Java 기반의 프레임워크을 활용한 웹 서버 구현'\n"
//            + "'- Spring WebSocket을 활용한 실시간 채팅 서버 구현' 이런식으로 출력해줘'\n"
//        );



    for (AiRequest tec : tecList) {
      prompt.append(tec.toString());
    }

    prompt.append(
        "출력은 JSON데이터 형태로 \n"
            + "{ 1.${primaryCategory} :{"
            + "    1) ${secondaryCategory} : {"
            + "        technology : 기술스택명,"
            + "           description : [ - 설명1, - 설명2] "
            + "} \n"
    );

    prompt.append("중복되거나 비슷한 내용이 있으면 합쳐서 요약해서 출력하고 없는 내용은 추가 안해도 돼, 예시는 빼고 출력해");

    String aiResponse = openAiChatModel.call(prompt.toString());
    return aiResponse;
  }

  public AnswerResponse processAiResponse(String aiResponse) {
    try {
      // ```json과 ``` 마크다운 표시 제거
      String cleanJson = aiResponse
          .replaceAll("```json\\s*", "")
          .replaceAll("```\\s*", "")
          .trim();

      // JSON을 TechnologyResponse 객체로 변환
      ObjectMapper mapper = new ObjectMapper();
      return mapper.readValue(cleanJson, AnswerResponse.class);

    } catch (JsonProcessingException e) {
      log.error("JSON 파싱 중 에러 발생", e);
      throw new RuntimeException("JSON 변환 실패", e);
    }
  }
}
