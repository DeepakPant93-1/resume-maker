package com.learning.resumemaker;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.openfeign.EnableFeignClients;

@SpringBootApplication
@EnableFeignClients
public class ResumemakerApplication {

	public static void main(String[] args) {
		SpringApplication.run(ResumemakerApplication.class, args);
	}

}
