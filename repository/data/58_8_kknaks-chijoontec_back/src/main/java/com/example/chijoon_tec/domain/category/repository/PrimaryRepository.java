package com.example.chijoon_tec.domain.category.repository;

import com.example.chijoon_tec.domain.category.entity.PrimaryCategory;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface PrimaryRepository extends JpaRepository<PrimaryCategory, Long> {

}
