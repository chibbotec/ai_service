package com.example.chijoon_tec.domain.tec.dto;


import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class TecRequest {
  private Long categoryId;
  private Long subCategoryId;
  private String technology;
  private String description;
  private String jobPosting;
  private String sourceURL;
}
