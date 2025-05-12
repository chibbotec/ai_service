package com.example.chijoon_tec.domain.tec.dto;

import com.example.chijoon_tec.domain.tec.entity.Tec;
import java.util.stream.Collectors;
import lombok.Builder;
import lombok.Data;
import lombok.Getter;

@Getter
@Builder
public class TecResponse {
    private Long id;
    private String primaryCategory;
    private String secondaryCategory;
    private String technology;
    private String description;
    private String jobPosting;
    private String sourceURL;

    public static TecResponse of(Tec tec){
      return TecResponse.builder()
        .id(tec.getId())
        .primaryCategory(tec.getPrimaryCategory().getPrimaryCategory())
        .secondaryCategory(tec.getSecondaryCategory().getSecondaryCategory())
        .technology(tec.getTechnology())
        .description(tec.getDescription())
        .jobPosting(tec.getJobPosting())
        .sourceURL(tec.getSourceURL())
        .build();
    }
}
