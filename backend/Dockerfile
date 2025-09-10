FROM jelastic/maven:3.9.5-openjdk-21 as builder

WORKDIR /app

COPY pom.xml ./

RUN mvn dependency:resolve dependency:resolve-sources dependency:resolve-plugins -B

COPY src ./src

RUN mvn clean package -DskipTests

FROM jelastic/maven:3.9.5-openjdk-21

WORKDIR /app

RUN mkdir -p /app/logs

COPY --from=builder /app/target/*.jar app.jar

RUN groupadd -r spring && useradd -r -g spring spring
RUN chown -R spring:spring /app
USER spring

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080/actuator/health || exit 1

ENTRYPOINT ["java", "-jar", "/app/app.jar"]
