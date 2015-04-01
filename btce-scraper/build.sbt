packSettings

packMain := Map("btce-scraper" -> "cryptovent.btce.scraper.App")

proguardSettings

ProguardKeys.proguardVersion in Proguard := "5.0"

ProguardKeys.options in Proguard ++= Seq("-dontnote", "-dontwarn", "-ignorewarnings")

ProguardKeys.options in Proguard += ProguardOptions.keepMain("cryptovent.btce.scraper.App")

name := "btce-scraper"

version := "0.1-SNAPSHOT"

organization := "divine-afflatus"

scalaVersion := "2.11.6"

scalacOptions ++= Seq("-deprecation", "-feature")

libraryDependencies ++= Seq(
  "org.scalaz" %% "scalaz-core" % "7.1.1",
  "org.spire-math" %% "spire" % "0.9.0",
  "com.chuusai" %% "shapeless" % "2.1.0",
  "com.typesafe.slick" %% "slick" % "2.1.0",
  "org.scalatest" %% "scalatest" % "2.1.3" % "test",
  "org.scalacheck" %% "scalacheck" % "1.12.2" % "test",
  "org.typelevel" %% "discipline" % "0.2.1" % "test")

libraryDependencies ++= Seq(
  "org.xerial" % "sqlite-jdbc" % "3.7.2",
  "org.jsoup" % "jsoup" % "1.7.3",
  "joda-time" % "joda-time" % "2.3",
  "org.joda" % "joda-convert" % "1.6",
  "org.slf4j" % "slf4j-api" % "1.7.7",
  "org.slf4j" % "slf4j-log4j12" % "1.7.7",
  "log4j" % "log4j" % "1.2.17"
)
