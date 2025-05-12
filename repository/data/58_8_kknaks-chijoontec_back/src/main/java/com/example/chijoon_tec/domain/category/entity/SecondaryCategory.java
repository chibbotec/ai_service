package com.example.chijoon_tec.domain.category.entity;

import static jakarta.persistence.GenerationType.IDENTITY;

import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.Id;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.OneToMany;
import java.util.List;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Entity
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SecondaryCategory {
  @Id
  @GeneratedValue(strategy = IDENTITY)
  private Long id;

  private String secondaryCategory;

  @ManyToOne
  private PrimaryCategory primaryCategory;
}
