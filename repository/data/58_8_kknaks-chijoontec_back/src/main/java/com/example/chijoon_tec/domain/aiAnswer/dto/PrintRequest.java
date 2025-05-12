package com.example.chijoon_tec.domain.aiAnswer.dto;


import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class PrintRequest {
  private String primaryCategory;
  private String secondaryCategory;
  private String technology;
  private String description;
  private String jobPosting;
  private String sourceURL;
}
