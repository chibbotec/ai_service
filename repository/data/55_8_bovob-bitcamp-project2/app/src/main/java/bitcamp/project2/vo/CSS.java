package bitcamp.project2.vo;

public class CSS {
  //ANSI SET
  public static final String dotCode = "\u25AE";
  public static final String redAnsi = "\033[31m";
  public static final String resetAnsi = "\033[0m";
  public static final String blueAnsi = "\033[94m";
  public static final String boldAnsi = "\033[1m";
  public static final String yellowAnsi = "\033[93m";
  public static final String line = "----------------------------------";
  public static final String longLine =
      "----------------------------------------------------------------------";

  public static final String boldRedAnsi = (boldAnsi) + (redAnsi);
  public static final String boldBlueAnsi = (boldAnsi) + (blueAnsi);
  public static final String boldYellowAnsi = (boldAnsi) + (yellowAnsi);
  public static final String boldLine = (boldAnsi) + (line);
  public static final String boldLongLine = (boldAnsi) + (longLine);

}
