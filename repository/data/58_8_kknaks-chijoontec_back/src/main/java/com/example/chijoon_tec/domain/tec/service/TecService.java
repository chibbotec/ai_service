package com.example.chijoon_tec.domain.tec.service;

import com.example.chijoon_tec.domain.category.entity.PrimaryCategory;
import com.example.chijoon_tec.domain.category.entity.SecondaryCategory;
import com.example.chijoon_tec.domain.category.repository.PrimaryRepository;
import com.example.chijoon_tec.domain.category.repository.SecondaryRepository;
import com.example.chijoon_tec.domain.tec.dto.TecRequest;
import com.example.chijoon_tec.domain.tec.entity.Tec;
import com.example.chijoon_tec.domain.tec.repository.TecRepository;
import java.util.List;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
@Slf4j
public class TecService {

  private final PrimaryRepository primaryRepository;
  private final SecondaryRepository secondaryRepository;
  private final TecRepository tecRepository;

  public Page<Tec> findAll(Pageable pageable) {
    return tecRepository.findAll(pageable);
  }

  public void addTec(TecRequest request) {
    PrimaryCategory primaryCategory = primaryRepository.findById(request.getCategoryId()).orElse(null);
    SecondaryCategory secondaryCategory = secondaryRepository.findById(request.getSubCategoryId()).orElse(null);
    Tec tec = Tec.builder()
        .primaryCategory(primaryCategory)
        .secondaryCategory(secondaryCategory)
        .technology(request.getTechnology())
        .description(request.getDescription())
        .jobPosting(request.getJobPosting())
        .sourceURL(request.getSourceURL())
        .build();
    tecRepository.save(tec);
  }

  public void addTecList(List<TecRequest> requestList) {
    log.debug("tecRequestList: {}", requestList);
    for (TecRequest request : requestList) {
      log.debug("======:{}", request.getCategoryId());
      PrimaryCategory primaryCategory = primaryRepository.findById(request.getCategoryId())
          .orElseThrow(() -> new IllegalArgumentException("Primary category not found"));

      SecondaryCategory secondaryCategory = secondaryRepository.findById(request.getSubCategoryId())
          .orElseThrow(() -> new IllegalArgumentException("Secondary category not found"));
      Tec tec = Tec.builder()
          .primaryCategory(primaryCategory)
          .secondaryCategory(secondaryCategory)
          .technology(request.getTechnology())
          .description(request.getDescription())
          .jobPosting(request.getJobPosting())
          .sourceURL(request.getSourceURL())
          .build();
      log.debug("tec:{}", tec.getDescription());
      tecRepository.save(tec);
    }
  }
}
