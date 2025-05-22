package bitcamp.project2.command;

import bitcamp.project2.Prompt.Prompt;
import bitcamp.project2.util.ArrayList;
import bitcamp.project2.vo.ToDoList;

import java.time.LocalDate;

public class DayOverCommand {
  public ToDoList toDoList;
  public ArrayList arr;

  public DayOverCommand() {
  }

  public DayOverCommand(ArrayList arr) {
    this.arr = arr;
  }

  public ToDoList excuteDayOverCommand(ToDoList toDoList) {
    while (true) {
      String command = Prompt.input("하루일과를 종료 하시겠습니까?(Y/N)");
      if (command.equalsIgnoreCase("Y")) {
        //ArrayList 추가
        arr.add(toDoList);
        //toDoList 초기화
        LocalDate date = toDoList.getDate();
        LocalDate tomorrow = LocalDate.of(date.getYear(), date.getMonth(), date.getDayOfMonth());
        tomorrow = tomorrow.plusDays(1);
        ToDoList newtoDoList = new ToDoList(tomorrow);
        System.out.println("저장 완료.");
        System.out.printf("%s로 넘어갑니다.\n", newtoDoList.getDate());
        return newtoDoList;
      } else if (command.equalsIgnoreCase("N")) {
        System.out.println("메인 메뉴로 돌아 갑니다.");
        return toDoList;
      } else {
        System.out.println("Y 나 N를 입력하세요");
      }
    }
  }

  public ArrayList getArray() {
    return this.arr;
  }
}
