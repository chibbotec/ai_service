package bitcamp.project2.command;

import bitcamp.project2.vo.Items;

import static bitcamp.project2.vo.CSS.*;


public class ShopCommand {
  // 아이템 가격
  public static int priceLateCoupon = 500;
  public static int priceSleepCoupon = 1000;
  public static int priceStudyCoupon = 100000000;
  public static int priceNightCoupon = 500000000;
  private final Items items;
  public ShopCommand(Items items) {
    this.items = items;
  }

  // 판매리스트
  public static void printShopInventory() {
    System.out.println("[아이템 판매 리스트]");
    System.out.printf("1.지각방지.......%10d 골드\n", priceLateCoupon);
    System.out.printf("2.졸음방지.......%10d 골드\n", priceSleepCoupon);
    System.out.printf("3.복습했다치기...%10d 골드\n", priceStudyCoupon);
    System.out.printf("4.야자출튀.......%10d 골드\n", priceNightCoupon);
  }

  public void executeShopCommand(String subTitle) {
    switch (subTitle) {
      case "지각방지":
        buyLateCoupon(subTitle);
        break;
      case "졸음방지":
        buySleepCoupon(subTitle);
        break;
      case "복습했다치기":
        buyStudyCoupon(subTitle);
        break;
      case "야자출튀":
        buyNightCoupon(subTitle);
        break;
    }
  }

  // 구매로직
  private void buyLateCoupon(String subTitle) {
    String ansiSubTitle = (boldBlueAnsi + subTitle + resetAnsi);
    if (items.getGold() < priceLateCoupon) {
      System.out.println("골드가 부족합니다.");
    } else {
      items.incrementCoupon(subTitle);
      items.decrementGold(priceLateCoupon);
      System.out.printf("[%s]를 구매했습니다.\n", ansiSubTitle);
    }
    printItemList();
  }

  private void buySleepCoupon(String subTitle) {
    String ansiSubTitle = (boldBlueAnsi + subTitle + resetAnsi);
    if (items.getGold() < priceSleepCoupon) {
      System.out.println("골드가 부족합니다.");
    } else {
      items.incrementCoupon(subTitle);
      items.decrementGold(priceSleepCoupon);
      System.out.printf("[%s]를 구매했습니다.\n", ansiSubTitle);
    }
    printItemList();
  }

  private void buyStudyCoupon(String subTitle) {
    String ansiSubTitle = (boldBlueAnsi + subTitle + resetAnsi);
    if (items.getGold() < priceStudyCoupon) {
      System.out.println("골드가 부족합니다.");
    } else {
      items.incrementCoupon(subTitle);
      items.decrementGold(priceStudyCoupon);
      System.out.printf("[%s]를 구매했습니다.\n", ansiSubTitle);
    }
    printItemList();
  }

  private void buyNightCoupon(String subTitle) {
    String ansiSubTitle = (boldBlueAnsi + subTitle + resetAnsi);
    if (items.getGold() < priceNightCoupon) {
      System.out.println("골드가 부족합니다.");
    } else {
      items.incrementCoupon(subTitle);
      items.decrementGold(priceNightCoupon);
      System.out.printf("[%s]를 구매했습니다.\n", ansiSubTitle);
    }
    printItemList();
  }

  // 아이템리스트
  public void printItemList() {
    System.out.println(boldLine);
    printShopInventory();
    System.out.println(boldLine);
    printItemInventory();
    System.out.println(boldLine);
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

}
