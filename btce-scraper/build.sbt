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

resolvers += Resolver.sonatypeRepo("public")

libraryDependencies ++= Seq(
  "org.scalaz" %% "scalaz-core" % "7.1.1",
  "org.scalaz" %% "scalaz-effect" % "7.1.1",
  "com.typesafe.slick" %% "slick" % "2.1.0",
  "com.github.scopt" %% "scopt" % "3.3.0",
  "org.xerial" % "sqlite-jdbc" % "3.7.2",
  "org.jsoup" % "jsoup" % "1.7.3")
