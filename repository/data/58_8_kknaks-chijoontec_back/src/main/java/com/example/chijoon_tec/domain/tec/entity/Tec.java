package com.example.chijoon_tec.domain.tec.entity;

import static jakarta.persistence.GenerationType.IDENTITY;

import com.example.chijoon_tec.domain.category.entity.PrimaryCategory;
import com.example.chijoon_tec.domain.category.entity.SecondaryCategory;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.Id;
import jakarta.persistence.ManyToOne;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Entity
@Getter
@Setter
@AllArgsConstructor
@NoArgsConstructor
@Builder
public class Tec {
  @Id
  @GeneratedValue(strategy = IDENTITY)
  private Long id;

  @ManyToOne
  private PrimaryCategory primaryCategory;

  @ManyToOne
  private SecondaryCategory secondaryCategory;

  private String technology;
  private String description;
  private String jobPosting;
  private String sourceURL;

}
