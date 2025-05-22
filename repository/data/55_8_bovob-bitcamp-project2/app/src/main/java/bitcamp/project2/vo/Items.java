package bitcamp.project2.vo;

import java.util.ArrayList;

public class Items {

  private int lateCoupon;
  private int sleepCoupon;
  private int studyCoupon;
  private int nightCoupon;
  private int gold=500;

  public int getLateCoupon() {
    return lateCoupon;
  }

  public void setLateCoupon(int lateCoupon) {
    this.lateCoupon = lateCoupon;
  }

  public int getSleepCoupon() {
    return sleepCoupon;
  }

  public void setSleepCoupon(int sleepCoupon) {
    this.sleepCoupon = sleepCoupon;
  }

  public int getStudyCoupon() {
    return studyCoupon;
  }

  public void setStudyCoupon(int studyCoupon) {
    this.studyCoupon = studyCoupon;
  }

  public int getNightCoupon() {
    return nightCoupon;
  }

  public void setNightCoupon(int nightCoupon) {
    this.nightCoupon = nightCoupon;
  }

  public void incrementCoupon(String coupon){
    switch (coupon){
      case "지각방지":
        this.lateCoupon += 1;
        break;
      case "졸음방지":
        this.sleepCoupon += 1;
        break;
      case "복습했다치기":
        this.studyCoupon += 1;
        break;
      case "야자출튀":
        this.nightCoupon += 1;
        break;
    }
  }

  public void decrementCoupon(String coupon){
    switch (coupon){
      case "지각방지":
        this.lateCoupon -= 1;
        break;
      case "졸음방지":
        this.sleepCoupon -= 1;
        break;
      case "복습했다치기":
        this.studyCoupon -= 1;
        break;
      case "야자출튀":
        this.nightCoupon -= 1;
        break;
    }
  }

  public int getGold() {
    return gold;
  }

  public void setGold(int gold) {
    this.gold = gold;
  }

  public void incrementGold(int amount){
    this.gold += amount;
  }
  public void decrementGold(int amount){
    this.gold -= amount;
  }

}
