package bitcamp.project2.command;

import bitcamp.project2.vo.Items;
import bitcamp.project2.vo.ToDoList;

public class CompleteCommand {
  private final Items items;


  public CompleteCommand(Items items) {
    this.items = items;
  }

  public void excuteCompleteCommand(String subTitle, ToDoList toDoList) {
    //    System.out.printf("[%s]\n", subTitle);
    switch (subTitle) {
      case "노지각":
        completeLate(subTitle, toDoList);
        break;
      case "노졸음":
        completeSleep(subTitle, toDoList);
        break;
      case "복습":
        completeStudy(subTitle, toDoList);
        break;
      case "야자":
        completeNight(subTitle, toDoList);
        break;
    }
  }

  void completeLate(String subTitle, ToDoList toDoList) {
    if (toDoList.isLate()) {
      System.out.printf("[%s]은(는) 이미 완료 했습니다.\n", subTitle);
    } else {
      toDoList.setLate(true);
      System.out.printf("[%s]을(를) 완료 했습니다.\n", subTitle);
      items.incrementGold(10);
      System.out.println("10 골드를 얻었습니다.");
      toDoList.setTodayComplete();
    }
  }

  void completeSleep(String subTitle, ToDoList toDoList) {
    if (toDoList.isSleep()) {
      System.out.printf("[%s]은(는) 이미 완료 했습니다.\n", subTitle);
    } else {
      toDoList.setSleep(true);
      System.out.printf("[%s]을(를) 완료 했습니다.\n", subTitle);
      items.incrementGold(20);
      System.out.println("20 골드를 얻었습니다.");
      toDoList.setTodayComplete();
    }
  }

  void completeStudy(String subTitle, ToDoList toDoList) {
    if (toDoList.isStudy()) {
      System.out.printf("[%s]은(는) 이미 완료 했습니다.\n", subTitle);
    } else {
      toDoList.setStudy(true);
      System.out.printf("[%s]을(를) 완료 했습니다.\n", subTitle);
      items.incrementGold(50);
      System.out.println("50 골드를 얻었습니다.");
      toDoList.setTodayComplete();
    }
  }

  void completeNight(String subTitle, ToDoList toDoList) {
    if (toDoList.isNight()) {
      System.out.printf("[%s]은(는) 이미 완료 했습니다.\n", subTitle);
    } else {
      toDoList.setNight(true);
      System.out.printf("[%s]을(를) 완료 했습니다.\n", subTitle);
      items.incrementGold(100);
      System.out.println("100 골드를 얻었습니다.");
      toDoList.setTodayComplete();
    }
  }
}
