package com.example.chijoon_tec.domain.category.entity;

import static jakarta.persistence.GenerationType.IDENTITY;

import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.Id;
import jakarta.persistence.OneToMany;
import java.util.List;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Entity
@Getter
@Setter
@NoArgsConstructor
public class PrimaryCategory {
  @Id
  @GeneratedValue(strategy = IDENTITY)
  private Long id;

  private String primaryCategory;

  @OneToMany
  private List<SecondaryCategory> secondaryCategories;

}
