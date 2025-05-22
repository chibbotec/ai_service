package bitcamp.project2.util;

import java.util.Calendar;

public class SearchCalendar {
  public static void printWeekCalendar(Calendar calendar) {
    // Calendar 인스턴스를 생성하고 연도, 월, 날짜를 설정
    //    Calendar calendar = Calendar.getInstance();
    //    calendar.set(Calendar.YEAR, year);
    //    calendar.set(Calendar.MONTH, month); // Calendar.MONTH는 0부터 시작
    //    calendar.set(Calendar.DAY_OF_MONTH, day);

    // 해당 날짜가 포함된 주의 첫 번째 날(일요일) 계산
    int dayOfWeek = calendar.get(Calendar.DAY_OF_WEEK);
    calendar.add(Calendar.DAY_OF_MONTH, Calendar.SUNDAY - dayOfWeek);

    // 주의 첫 번째 날로 설정된 calendar에서 연도와 월을 가져옴
    int startYear = calendar.get(Calendar.YEAR);
    int startMonth = calendar.get(Calendar.MONTH);

    //    System.out.println(year + "년 " + month + "월 " + day + "일이 포함된 주");
    System.out.println("일 월 화 수 목 금 토");

    // 첫 번째 줄의 빈칸 (첫 번째 날이 이전 월에 속할 경우)
    for (int i = Calendar.SUNDAY; i < calendar.get(Calendar.DAY_OF_WEEK); i++) {
      System.out.print("   ");
    }

    // 날짜 출력
    for (int i = 0; i < 7; i++) {
      if (calendar.get(Calendar.YEAR) == startYear && calendar.get(Calendar.MONTH) == startMonth) {
        int currentDay = calendar.get(Calendar.DAY_OF_MONTH);
        System.out.printf("%2d ", currentDay);
      } else {
        System.out.print("   ");
      }

      calendar.add(Calendar.DAY_OF_MONTH, 1);
    }
    System.out.println();
  }
}
