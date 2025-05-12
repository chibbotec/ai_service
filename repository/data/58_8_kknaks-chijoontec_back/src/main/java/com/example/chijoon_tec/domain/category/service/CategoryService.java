package com.example.chijoon_tec.domain.category.service;

import com.example.chijoon_tec.domain.category.dto.CategoryRequest;
import com.example.chijoon_tec.domain.category.entity.PrimaryCategory;
import com.example.chijoon_tec.domain.category.entity.SecondaryCategory;
import com.example.chijoon_tec.domain.category.repository.SecondaryRepository;
import com.example.chijoon_tec.domain.category.repository.PrimaryRepository;
import java.util.List;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class CategoryService {

  private final PrimaryRepository primaryRepository;
  private final SecondaryRepository secondaryRepository;

  public List<PrimaryCategory> getPrimaryList() {
    return primaryRepository.findAll();
  }

  public List<SecondaryCategory> getSecondaryList(Long selectedCategoryId) {
    return secondaryRepository.findSecondaryCategoryByPrimaryCategoryId(selectedCategoryId);
  }

  public void addSecondaryCategory(Long categoryId, CategoryRequest request) {
    PrimaryCategory primaryCategory = primaryRepository.findById(categoryId)
        .orElseThrow(() -> new IllegalArgumentException("Primary category not found"));
    SecondaryCategory secondaryCategory = SecondaryCategory.builder()
        .primaryCategory(primaryCategory)
        .secondaryCategory(request.getName())
        .build();
    secondaryRepository.save(secondaryCategory);
  }
}
