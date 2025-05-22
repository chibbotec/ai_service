package bitcamp.project2;

import bitcamp.project2.Prompt.Prompt;
import bitcamp.project2.command.*;
import bitcamp.project2.util.ArrayList;
import bitcamp.project2.vo.Items;
import bitcamp.project2.vo.ToDoList;

import java.time.LocalDate;

import static bitcamp.project2.vo.CSS.*;

public class App {
  public static ArrayList arrList = new ArrayList();
  public static String[][] subMenus = {{"노지각", "노졸음", "복습", "야자"}, // 과업완료하기
      {"지각방지", "졸음방지", "복습했다치기", "야자출튀"}, // 아이템사용
      {"지각방지", "졸음방지", "복습했다치기", "야자출튀"}, // 상점가기
      {"주별조회", "일별조회"}};// 업적조회
  static String[] mainMenus = new String[] {"과업완료하기", "아이템사용", "상점가기", "업적조회", "일과종료", "포기하기"};
  static Items items = new Items();
  public ToDoList toDoList = new ToDoList(LocalDate.now());
  public CompleteCommand completeCommand = new CompleteCommand(items);
  public ItemCommand itemCommand = new ItemCommand(items);
  public ShopCommand shopCommand = new ShopCommand(items);
  public ViewCommand viewCommand = new ViewCommand(arrList);
  public DayOverCommand dayOverCommand = new DayOverCommand(arrList);

  public static void main(String[] args) {
    Test test = new Test();
    test.addTest(arrList);
    App app = new App();
    app.execute();
  }

  static boolean isValidateMenu(int menuNo, String[] menus) {
    return menuNo >= 1 && menuNo <= menus.length;
  }

  static String getMenuTitle(int menuNo, String[] menus) {
    return isValidateMenu(menuNo, menus) ? menus[menuNo - 1] : null;
  }

  public static void printTodayDoitList(ToDoList toDoList) {
    System.out.println(boldLine);
    System.out.println(boldAnsi + "오늘 할일" + resetAnsi);
    System.out.printf("노 지 각 :  %s\n", toDoAnsi(toDoList.isLate()));
    System.out.printf("노 졸 음 :  %s\n", toDoAnsi(toDoList.isSleep()));
    System.out.printf("복    습 :  %s\n", toDoAnsi(toDoList.isStudy()));
    System.out.printf("야    자 :  %s\n", toDoAnsi(toDoList.isNight()));
    System.out.println(boldLine);
  }

  public static String toDoAnsi(Boolean bool) {
    return bool ?
        String.format("%s%s%s", boldBlueAnsi, "완료", resetAnsi) :
        String.format("%s%s%s", boldRedAnsi, "미완", resetAnsi);
  }

  void printSubMenu(String menuTitle, String[] menus) {
    if (menuTitle.equals("아이템사용") | menuTitle.equals("상점가기")) {
      itemCommand.printItemMenus(menuTitle, menus);
    } else {
      System.out.printf("[%s]\n", menuTitle);
      for (int i = 0; i < menus.length; i++) {
        System.out.printf("%d. %s\n", i + 1, menus[i]);
      }
      System.out.println("9. 이전");
    }
  }

  void printMainMenu() {
    String appTitle = "      [스파르타 공부법]";
    System.out.println(boldLine);
    System.out.println(boldAnsi + appTitle + resetAnsi);
    App.printTodayDoitList(toDoList);
    System.out.println(toDoList.getDate());
    System.out.printf("Today : %4.1f%%  ", toDoList.getTodayComplete());
    printGraph(toDoList.getTodayComplete(), "today");
    toDoList.setTotalComplete(arrList.getAverage());
    System.out.printf("Total : %4.1f%%  ", toDoList.getTotalComplete());
    printGraph(toDoList.getTotalComplete(), "total");
    System.out.println(boldLine);

    // 오늘 할일 메소드 출력
    for (int i = 0; i < mainMenus.length; i++) {
      if (mainMenus[i].equals("포기하기")) {
        System.out.printf("%s%d. %s%s\n", (boldRedAnsi), (i + 1), mainMenus[i], resetAnsi);
      } else {
        System.out.printf("%d. %s\n", (i + 1), mainMenus[i]);
      }
    }
    System.out.println(boldLine);
  }

  void execute() {
    String command;
    while (true) {
      printMainMenu();
      try {
        if (toDoList.getTotalComplete() < 20) {
          System.out.println("Game Over 당신은 훈련수당을 받을 수 없습니다.");
          break;
        }
        command = Prompt.input("메인> ");
        if (command.equals("menu")) {
          printMainMenu();
          continue;
        }
        int menuNo = Integer.parseInt(command);
        String menuTitle = getMenuTitle(menuNo, mainMenus);
        if (menuTitle == null) {
          System.out.println("유효한 메뉴 번호가 아닙니다.");
        } else if (menuTitle.equals("포기하기")) {
          System.out.println("Game Over 당신은 훈련수당을 받을 수 없습니다.");
          break;
        } else if (menuTitle.equals("일과종료")) {
          toDoList = dayOverCommand.excuteDayOverCommand(toDoList);
        } else {
          processSubMenu(menuTitle, subMenus[menuNo - 1]);
        }
      } catch (NumberFormatException ex) {
        System.out.println("숫자로 메뉴 번호를 입력하세요.");
      }
    }
    System.out.println("종료합니다.");
    Prompt.close();
  }

  void processSubMenu(String menuTitle, String[] menus) {
    printSubMenu(menuTitle, menus);
    while (true) {
      String command = Prompt.input("메인/%s> ", menuTitle);
      if (command.equals("menu")) {
        printSubMenu(menuTitle, menus);
        continue;
      } else if (command.equals("9")) {
        break;
      }
      try {
        int subMenuNo = Integer.parseInt(command);
        String subMenuTitle = getMenuTitle(subMenuNo, menus);
        if (subMenuTitle == null) {
          System.out.println("유효한 메뉴 번호가 아닙니다.");
        } else {
          switch (menuTitle) {
            case "과업완료하기":
              completeCommand.excuteCompleteCommand(subMenuTitle, toDoList);
              break;
            case "아이템사용":
              itemCommand.executeItemCommand(subMenuTitle, toDoList);
              break;
            case "상점가기":
              shopCommand.executeShopCommand(subMenuTitle);
              break;
            case "업적조회":
              viewCommand.excuteViewCommand(subMenuTitle, toDoList);
              break;
          }
        }
      } catch (NumberFormatException ex) {
        System.out.println("숫자로 메뉴 번호를 입력하세요.");
      }
    }

  }

  public void printGraph(float total, String day) {
    int barLength = 18;
    double ratio = total == 0 ? 0 : total / 100.0f;
    int filledLength = (int) (ratio * barLength);

    switch (day) {
      case "today":
        for (int i = 0; i < filledLength; i++) {
          System.out.printf("%s%s%s", blueAnsi, dotCode, resetAnsi);
        }
        break;
      case "total":
        for (int i = 0; i < filledLength; i++) {
          System.out.printf("%s%s%s", redAnsi, dotCode, resetAnsi);
        }
        break;
    }
    System.out.println();
  }
}


