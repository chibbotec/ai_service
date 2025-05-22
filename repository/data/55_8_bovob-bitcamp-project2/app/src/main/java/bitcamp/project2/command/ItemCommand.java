package bitcamp.project2.command;

import bitcamp.project2.vo.Items;
import bitcamp.project2.vo.ToDoList;

import static bitcamp.project2.vo.CSS.*;


public class ItemCommand {

  private static Items items;

  public ItemCommand(Items items) {
    ItemCommand.items = items;
  }

  public void printItemMenus(String menuTitle, String[] menus) {
    String appTitle = "             [아이템]";
    System.out.println(boldLine);
    System.out.println(boldAnsi + appTitle + resetAnsi);
    System.out.println(boldLine);
    if (menuTitle.equals("상점가기")) {
      ShopCommand.printShopInventory();

      System.out.println(boldLine);
    }
    printItemInventory();
    System.out.println(boldLine);
    System.out.println("9. 이전");
    System.out.println(boldLine);
  }

  // 메뉴실행
  public void executeItemCommand(String subTitle, ToDoList toDoList) {

    switch (subTitle) {
      case "지각방지":
        useLateCoupon(subTitle, toDoList);
        break;
      case "졸음방지":
        useSleepCoupon(subTitle, toDoList);
        break;
      case "복습했다치기":
        useStudyCoupon(subTitle, toDoList);
        break;
      case "야자출튀":
        useNightCoupon(subTitle, toDoList);
        break;
    }
  }

  // 아이템(쿠폰)사용
  private void useLateCoupon(String subTitle, ToDoList toDoList) {
    if (toDoList.isLate()) {
      System.out.println("이미 달성하여 사용할 수 없습니다.");
    } else {
      checkItem(subTitle, toDoList);
    }
    printItemList(toDoList);
  }

  private void useSleepCoupon(String subTitle, ToDoList toDoList) {
    if (toDoList.isSleep()) {
      System.out.println("이미 달성하여 사용할 수 없습니다.");
    } else {
      checkItem(subTitle, toDoList);
    }
    printItemList(toDoList);
  }

  private void useStudyCoupon(String subTitle, ToDoList toDoList) {
    if (toDoList.isStudy()) {
      System.out.println("이미 달성하여 사용할 수 없습니다.");
    } else {
      checkItem(subTitle, toDoList);
    }
    printItemList(toDoList);
  }

  private void useNightCoupon(String subTitle, ToDoList toDoList) {
    if (toDoList.isNight()) {
      System.out.println("이미 달성하여 사용할 수 없습니다.");
    } else {
      checkItem(subTitle, toDoList);
    }
    printItemList(toDoList);
  }

  // 아이템체크
  public void checkItem(String subTitle, ToDoList toDoList) {
    String ansiSubTitle = (boldAnsi + subTitle + resetAnsi);

    switch (subTitle) {
      case "지각방지":
        if (items.getLateCoupon() == 0) {
          System.out.println("아이템이 없습니다.");
          break;
        } else {
          items.decrementCoupon(subTitle);
          toDoList.setLate(true);
          System.out.printf("[%s]을(를) 사용하였습니다.\n", ansiSubTitle);
        }
        break;
      case "졸음방지":
        if (items.getSleepCoupon() == 0) {
          System.out.println("아이템이 없습니다.");
          break;
        } else {
          items.decrementCoupon(subTitle);
          toDoList.setSleep(true);
          System.out.printf("[%s]을(를) 사용하였습니다.\n", ansiSubTitle);
        }
        break;
      case "복습했다치기":
        if (items.getStudyCoupon() == 0) {
          System.out.println("아이템이 없습니다.");
          break;
        } else {
          items.decrementCoupon(subTitle);
          toDoList.setStudy(true);
          System.out.printf("[%s]을(를) 사용하였습니다.\n", ansiSubTitle);
        }
        break;
      case "야자출튀":
        if (items.getNightCoupon() == 0) {
          System.out.println("아이템이 없습니다.");
          break;
        } else {
          items.decrementCoupon(subTitle);
          toDoList.setNight(true);
          System.out.printf("[%s]을(를) 사용하였습니다.\n", ansiSubTitle);
        }
        break;
    }
  }

  // 아이템리스트
  public void printItemInventory() {
    System.out.println("[아이템 리스트]");
    System.out.printf("1.지각방지.......%4d 개\n", items.getLateCoupon());
    System.out.printf("2.졸음방지.......%4d 개\n", items.getSleepCoupon());
    System.out.printf("3.복습했다치기...%4d 개\n", items.getStudyCoupon());
    System.out.printf("4.야자출튀.......%4d 개\n", items.getNightCoupon());
    System.out.println(boldLine);
    printGold();
  }

  // 골드
  public void printGold() {
    String goldString = (boldYellowAnsi + items.getGold() + resetAnsi);
    System.out.printf("현재 보유골드는 [ %s ] 입니다. \n", goldString);
  }

  // 현재할일현황 변경
  public void printItemList(ToDoList toDoList) {
    System.out.println(boldLine);
    bitcamp.project2.App.printTodayDoitList(toDoList);
    System.out.println(boldLine);
    printItemInventory();
    System.out.println(boldLine);
  }
}
