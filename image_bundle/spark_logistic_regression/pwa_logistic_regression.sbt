name := "PWA Logistic Regression"

version := "1.0"

scalaVersion := "2.11.7"

libraryDependencies ++= Seq(
  "org.apache.spark"  % "spark-core_2.11"              % "2.0.0" % "provided",
  "org.apache.spark"  % "spark-sql_2.11"               % "2.0.0" % "provided",
  "org.apache.spark"  % "spark-mllib_2.11"             % "2.0.0" % "provided"
  )