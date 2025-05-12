package com.example.chijoon_tec.domain.aiAnswer.controller;

import com.example.chijoon_tec.domain.aiAnswer.dto.AnswerResponse;
import com.example.chijoon_tec.domain.aiAnswer.dto.PrintRequest;
import com.example.chijoon_tec.domain.aiAnswer.service.OpenAiService;
import java.util.List;
import java.util.stream.Collectors;
import lombok.NoArgsConstructor;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequiredArgsConstructor
@Slf4j
public class AiAnswer {

  private final OpenAiService openAiService;

  @PostMapping("/aiAnswer/print")
  public String print(
      @RequestBody List<PrintRequest> request){
    log.debug("request: {}", request.get(0).getPrimaryCategory());
    String response = openAiService.summarizeData(request);
    log.debug("response: {}", response);

    return response;



//    return request.stream()
//        .map(printRequest -> AnswerResponse.builder()
//            .primaryCategory(1L)
//            .secondaryCategory(1L)
//            .technology(printRequest.getTechnology())
//            .description(printRequest.getDescription())
//            .jobPosting(printRequest.getJobPosting())
//            .sourceURL(printRequest.getSourceURL())
//            .build())
//        .collect(Collectors.toList());
  }
}
