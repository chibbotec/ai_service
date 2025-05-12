package com.example.chijoon_tec.domain.tec.repository;

import com.example.chijoon_tec.domain.tec.entity.Tec;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface TecRepository extends JpaRepository<Tec, Integer> {
}
