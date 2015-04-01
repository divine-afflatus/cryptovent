package cryptovent.btce.scraper

import org.jsoup.Jsoup
import org.jsoup.nodes.Document

import org.joda.time.DateTime
import org.joda.time.format.DateTimeFormat

import org.slf4j.Logger
import org.slf4j.LoggerFactory

import scala.collection.JavaConverters._
import scala.util.{ Try, Success, Failure }
import scala.util.control.NonFatal
import org.apache.log4j.{Level, LogManager}

case class ChatMessage(id: Long, time: Long, name: String, text: String)

class SiteApi {
  private final val logger = LoggerFactory.getLogger(classOf[SiteApi])
  private final val SiteUrl = "http://trollboxarchive.com"
  private final val IndexUrl = SiteUrl + "/index.php"
  private final val QuoteUrl = SiteUrl + "/quote24.php"
  private final val TimeFormatter = DateTimeFormat.forPattern("yyyy-MM-dd HH:mm:ss").withZoneUTC()

  def page(index: Long): Try[Document] = {
    val connection = Try(Jsoup.connect(IndexUrl))
    connection.map { _.data("page", index.toString) }
    connection.map { _.execute().parse() }
  }

  def scrape(doc: Document): List[ChatMessage] =
    for (
      row <- doc.select(".chat-record-row").iterator.asScala.toList;
      id = row.attr("id").toLong;
      name = row.child(0).text();
      timeRaw = row.child(2).child(0).attr("data-time");
      time = DateTime.parse(timeRaw, TimeFormatter).getMillis;
      text = row.child(3).text()
    ) yield ChatMessage(id, time, name, text)
}

object App {
  import scala.slick.driver.SQLiteDriver.simple._
  import scala.slick.jdbc.meta.MTable

  class Messages(tag: Tag) extends Table[ChatMessage](tag, "messages") {
    def id = column[Long]("id", O.PrimaryKey) // This is the primary key column
    def time = column[Long]("time")
    def name = column[String]("name")
    def text = column[String]("text")

    // Every table needs a * projection with the same type as the table's type parameter
    def * = (id, time, name, text) <> (ChatMessage.tupled, ChatMessage.unapply)
  }
  val messages = TableQuery[Messages]

  def retry[T](times: Int)(func: => Try[T]): Try[T] = {
    require(times > 0)

    var result: Try[T] = null
    var count = 0

    while (count < times) {
      result = func
      if (result.isSuccess) {
        count = times - 1
      }
      count += 1
    }

    result
  }

  def main(args: Array[String]): Unit = {
    val api = new SiteApi

    Database.forURL("jdbc:sqlite:messages.db", driver = "org.sqlite.JDBC") withSession { implicit session =>
      if (MTable.getTables("messages").list.isEmpty) {
        messages.ddl.create
      }

      for (i <- 0L until 30000L) {
        var count = 0
        retry(5) { api.page(i) } match {
          case Success(doc) =>
            for (message <- api.scrape(doc)) {
              if (messages.filter(_.id === message.id).length.run == 0) {
                messages += message
                count += 1
              }
            }
          case Failure(e) =>
            println(e.getMessage)
            e.printStackTrace()
        }
        println(s"Found $count new messages on page $i.")
      }
    }
  }
}
