package bitcamp.project2.command;

import bitcamp.project2.App;
import bitcamp.project2.Prompt.Prompt;
import bitcamp.project2.util.ArrayList;
import bitcamp.project2.vo.ToDoList;

import java.time.DayOfWeek;
import java.time.LocalDate;

import static bitcamp.project2.vo.CSS.boldLine;
import static bitcamp.project2.vo.CSS.boldLongLine;



public class ViewCommand {
  public ArrayList arr;

  public ViewCommand(ArrayList arr) {
    this.arr = arr;
  }

  public void excuteViewCommand(String subTitle, ToDoList toDoList) {
    //        System.out.printf("[%s]\n", subTitle);
    switch (subTitle) {
      case "주별조회":
        viewWeek(toDoList);
        break;

      case "일별조회":
        viewDay(toDoList);
        break;
    }
  }

  private void viewWeek(ToDoList toDoList) {
    System.out.println(boldLongLine);

    if (arr.size() != 0) {
      LocalDate[] week = getWeek(toDoList);
      System.out.printf("조회 기준일 : %s\n", toDoList.getDate());
      System.out.print("| 날      짜 |");
      for (LocalDate date : week) {
        System.out.printf(" %1$tm-%1$td |", date);
      }
      System.out.println();

      System.out.print("| 당일달성률 |");
      for (LocalDate localDate : week) {
        Object obj = arr.getToDoList(localDate);
        ToDoList toDDo = (ToDoList) obj;
        if (toDDo != null) {
          System.out.printf(" %5.1f |", toDDo.getTodayComplete());
        } else {
          System.out.print("       |");
        }
      }

      System.out.println();
      System.out.print("| 누적달성률 |");
      for (LocalDate localDate : week) {
        Object obj = arr.getToDoList(localDate);
        ToDoList toDDo = (ToDoList) obj;
        if (toDDo != null) {
          System.out.printf(" %5.1f |", toDDo.getTotalComplete());
        } else {
          System.out.print("       |");
        }
      }
      System.out.println();
    }
    System.out.println(boldLongLine);

  }

  private void viewDay(ToDoList toDoList) {
    LocalDate findDate = Prompt.inputDate("조회일(yyyy-MM-dd)?");
    System.out.println(boldLine);
    Object obj = arr.getToDoList(findDate);
    System.out.println(boldLine);
    ToDoList toDo = (ToDoList) obj;
    if (toDo != null) {
      System.out.printf("조 회 일 : %s\n", findDate);
      App.printTodayDoitList(toDo);
      System.out.printf("Today : %4.1f%%  \n", toDo.getTodayComplete());
      System.out.printf("Total : %4.1f%%  \n", toDo.getTotalComplete());

    } else {
      System.out.println("해당 날짜에는 공부를 안햇습니다.");
    }
    System.out.println(boldLine);


  }

  private LocalDate[] getWeek(ToDoList toDoList) {
    LocalDate[] week = new LocalDate[7];
    LocalDate today = toDoList.getDate();

    LocalDate startOfWeek = today.with(DayOfWeek.MONDAY);
    LocalDate endOfWeek = today.with(DayOfWeek.SUNDAY);

    LocalDate current = startOfWeek;
    int index = 0;
    while (!current.isAfter(endOfWeek)) {
      week[index++] = current;
      current = current.plusDays(1);
    }
    return week;
  }
}
