package com.example.chijoon_tec.domain.aiAnswer.dto;

import com.example.chijoon_tec.domain.tec.entity.Tec;
import java.util.HashMap;
import java.util.Map;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@NoArgsConstructor
public class AnswerResponse {
    private Map<String, Map<String, TechDetail>> categories = new HashMap<>();

    @Getter
    @Setter
    @NoArgsConstructor
    public static class TechDetail {
        private String description;
        private String jobPosting;
        private String sourceURL;
    }
}
