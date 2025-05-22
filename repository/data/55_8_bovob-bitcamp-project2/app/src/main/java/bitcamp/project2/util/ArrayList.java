package bitcamp.project2.util;

import bitcamp.project2.vo.ToDoList;

import java.time.LocalDate;
import java.util.Arrays;

public class ArrayList {

  private static final int MAX_SIZE = 3;
  private int size;
  private Object[] list = new Object[MAX_SIZE];

  public void add(Object obj) {
    if (size == list.length) {
      //grow();
      int oldSize = list.length;
      int newSize = oldSize + (oldSize >> 1);
      list = Arrays.copyOf(list, newSize);
    }
    list[size++] = obj;
  }

  private void grow() {
    int oldSize = list.length;
    int newSize = oldSize + (oldSize >> 1);
    Object[] arr = new Object[newSize];
    System.arraycopy(list, 0, arr, 0, oldSize);
    list = arr;
  }

  public Object remove(int index) {
    if (index < 0 || index >= size) {
      return null;
    }
    Object deletedObj = list[index];
    for (int i = index + 1; i < size; i++) {
      list[i - 1] = list[i];
    }
    list[--size] = null;
    return deletedObj;
  }

  public Object[] toArray() {
    Object[] arr = new Object[size];
    System.arraycopy(list, 0, arr, 0, arr.length);
    return arr;
  }

  public int indexOf(Object obj) {
    for (int i = 0; i < size; i++) {
      if (list[i].equals(obj)) {
        return i;
      }
    }
    return -1;
  }

  public Object get(int index) {
    if (index < 0 || index >= size) {
      return null;
    }
    return list[index];
  }

  public boolean contains(Object obj) {
    return indexOf(obj) != -1;
  }

  public int size() {
    return size;
  }

  public Object getToDoList(LocalDate date) {
    for (Object obj : this.toArray()) {
      ToDoList toDoList = (ToDoList) obj;
      if (toDoList.getDate().isEqual(date)) {
        return obj;
      }
    }
    return null;
  }

  public float getAverage() {
    float sum = 0;
    int counter = 0;
    for (Object obj : this.toArray()) {
      counter++;
      ToDoList toDoList = (ToDoList) obj;
      sum += toDoList.getTodayComplete();
    }
    return counter != 0 ? sum / counter : 0;
  }

}


