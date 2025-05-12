package com.example.chijoon_tec.domain.category.controller;

import com.example.chijoon_tec.domain.category.dto.CategoryDto;
import com.example.chijoon_tec.domain.category.dto.CategoryRequest;
import com.example.chijoon_tec.domain.category.service.CategoryService;
import java.util.List;
import java.util.stream.Collectors;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequiredArgsConstructor
@RequestMapping("/category")
@Slf4j
public class CategoryController {
  private final CategoryService categoryService;

  @GetMapping("/primary")
  public List<CategoryDto> getPrimaryCategories(){
    return categoryService.getPrimaryList().stream()
        .map(category -> new CategoryDto(category.getId(),category.getPrimaryCategory()))
        .collect(Collectors.toList());
  }

  @GetMapping("/secondary/{primaryId}")
  public List<CategoryDto> getSecondaryCategories(
      @PathVariable("primaryId") Long selectedCategoryId){
    log.debug("selectedCategoryId : {}",selectedCategoryId);
    return categoryService.getSecondaryList(selectedCategoryId).stream()
        .map(category -> new CategoryDto(category.getId(),category.getSecondaryCategory()))
            .collect(Collectors.toList());
  }

  @PostMapping("/secondary/{categoryId}")
  public void addSecondaryCategory(
      @PathVariable("categoryId") Long categoryId,
      @RequestBody CategoryRequest request){
    categoryService.addSecondaryCategory(categoryId, request);
  }
}
