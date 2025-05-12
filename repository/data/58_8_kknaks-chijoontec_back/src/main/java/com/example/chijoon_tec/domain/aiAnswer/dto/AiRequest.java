package com.example.chijoon_tec.domain.aiAnswer.dto;

import static jakarta.persistence.GenerationType.IDENTITY;

import com.example.chijoon_tec.domain.category.entity.PrimaryCategory;
import com.example.chijoon_tec.domain.category.entity.SecondaryCategory;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;

@Data
@AllArgsConstructor
@Builder
public class AiRequest {
  private Long id;
  private String primaryCategory;
  private String secondaryCategory;
  private String technology;
  private String description;
  private String jobPosting;
  private String sourceURL;

  @Override
  public String toString(){
    return String.format(
        "primaryCategory: %s\n" +
            "secondaryCategory: %s\n" +
            "technology: %s\n" +
            "description: %s\n" +
            "jobPosting: %s\n" +
            "sourceURL: %s",
        primaryCategory,
        secondaryCategory,
        technology,
        description,
        jobPosting,
        sourceURL
    );
  }
}
