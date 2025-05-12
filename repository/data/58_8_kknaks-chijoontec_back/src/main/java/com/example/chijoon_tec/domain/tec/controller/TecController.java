package com.example.chijoon_tec.domain.tec.controller;

import com.example.chijoon_tec.domain.tec.dto.TecRequest;
import com.example.chijoon_tec.domain.tec.dto.TecResponse;
import com.example.chijoon_tec.domain.tec.entity.Tec;
import com.example.chijoon_tec.domain.tec.repository.TecRepository;
import com.example.chijoon_tec.domain.tec.service.TecService;
import java.util.stream.Collectors;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.web.PageableDefault;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequiredArgsConstructor
@Slf4j
public class TecController {

  private final TecService tecService;

  @GetMapping
  public Page<TecResponse> getAllTec(
      @PageableDefault(size=10) Pageable pageable
  ) {
    return tecService.findAll(pageable).map(TecResponse::of);
  }

  @PostMapping
  public void addTec(@RequestBody TecRequest tecRequest){
    tecService.addTec(tecRequest);
  }

  @PostMapping("/bulk")
  public void addTecList(@RequestBody List<TecRequest> tecRequestList){
    log.debug("tecRequestList: {}", tecRequestList);
    log.debug("tecRequestList size: {}", tecRequestList.size());
    tecService.addTecList(tecRequestList);
  }
}
