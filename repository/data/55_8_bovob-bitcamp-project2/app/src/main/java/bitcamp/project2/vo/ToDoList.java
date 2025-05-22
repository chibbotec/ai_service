package bitcamp.project2.vo;

import java.time.LocalDate;

public class ToDoList {
  private LocalDate date;
  private boolean late;
  private boolean sleep;
  private boolean study;
  private boolean night;
  private float todayComplete;
  private float totalComplete;

  public ToDoList() {
  }

  public ToDoList(LocalDate date) {
    this.date = date;
  }

  public void setTodayComplete() {
    float sum = 0;
    if (this.isSleep())
      sum += 1;
    if (this.isStudy())
      sum += 1;
    if (this.isNight())
      sum += 1;
    if (this.isLate())
      sum += 1;
    this.todayComplete = sum / 4 * 100;
  }

  public float getTodayComplete() {
    return todayComplete;
  }

  public float getTotalComplete() {
    return totalComplete;
  }

  public void setTotalComplete(float avg) {
    this.totalComplete = avg;
  }

  public LocalDate getDate() {
    return date;
  }

  public void setDate(LocalDate date) {
    this.date = date;
  }

  public boolean isLate() {
    return late;
  }

  public void setLate(boolean late) {
    this.late = late;
  }

  public boolean isSleep() {
    return sleep;
  }

  public void setSleep(boolean sleep) {
    this.sleep = sleep;
  }

  public boolean isStudy() {
    return study;
  }

  public void setStudy(boolean study) {
    this.study = study;
  }

  public boolean isNight() {
    return night;
  }

  public void setNight(boolean night) {
    this.night = night;
  }
}
