package com.example.chijoon_tec.domain.category.repository;

import com.example.chijoon_tec.domain.category.entity.SecondaryCategory;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface SecondaryRepository extends JpaRepository<SecondaryCategory, Long> {

  List<SecondaryCategory> findSecondaryCategoryByPrimaryCategoryId(Long selectedCategoryId);
}
