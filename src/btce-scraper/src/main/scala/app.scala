package cryptovent.btce.scraper

import org.jsoup.Jsoup
import org.jsoup.nodes.Document

import scala.annotation.tailrec
import scala.collection.JavaConverters._
import scala.slick.driver.{ JdbcProfile, SQLiteDriver }
import scala.slick.jdbc.meta.MTable
import scala.util.control.NonFatal
import scalaz._
import scalaz.effect._

case class ChatMessage(id: Long, time: Long, name: String, text: String)

object SiteApi {
  def pageUrl(number: Long): String = "http://trollboxarchive.com/page/" + number.toString

  def page(index: Long): \/[Throwable, Document] =
    try \/-(Jsoup.connect(pageUrl(index))
                 .execute()
                 .parse()) catch {
      case NonFatal(e) => -\/(e)
    }

  def scrape(doc: Document): List[ChatMessage] =
    for {
      row <- doc.select(".chat-record-message-area").iterator.asScala.toList
      name_link = row.child(0)
      message_span = row.child(1)
      date_span = row.child(2).select(".chat-record-date").iterator.asScala.toList.head

      id = message_span.attr("data-chatid").toLong
      name = name_link.text().split(":")(0)
      time = date_span.attr("data-time").toLong / 1000
      text = message_span.text()
    } yield ChatMessage(id, time, name, text)
}

class Scheme(val driver: JdbcProfile) {
  import driver.simple._

  class Messages(tag: Tag) extends Table[ChatMessage](tag, "messages") {
    def id = column[Long]("id", O.PrimaryKey) // This is the primary key column
    def time = column[Long]("time")
    def name = column[String]("name")
    def text = column[String]("text")

    // Every table needs a * projection with the same type as the table's type parameter
    def * = (id, time, name, text) <> (ChatMessage.tupled, ChatMessage.unapply)
  }
  val messages = TableQuery[Messages]

  def create(implicit session: Session): Unit = messages.ddl.create
  def tableExists(implicit session: Session): Boolean = !MTable.getTables("messages").list.isEmpty

  def filterNew(list: List[ChatMessage])(implicit session: Session): List[ChatMessage] = for {
    message <- list
    if !messages.filter(_.id === message.id).exists.run
  } yield message

  def insertAll(list: List[ChatMessage])(implicit session: Session): Unit = {
    messages ++= list
  }
}

case class Config(startPage: Long = -1, db: String = "")

object App {
  import scala.slick.jdbc.JdbcBackend.{ Database, Session }

  def retry[U, V](times: Int)(func: => U \/ V): U \/ V = {
    require(times > 0)

    @tailrec def retry0(times: Int, last: U \/ V): U \/ V = last match {
      case -\/(e) if times > 0 => retry0(times - 1, func)
      case x => x
    }

    retry0(times - 1, func)
  }

  def main(args: Array[String]): Unit = {
    val scheme = new Scheme(SQLiteDriver)

    Database.forURL("jdbc:sqlite:messages.db", driver = "org.sqlite.JDBC") withSession { implicit session =>
      if (!scheme.tableExists) scheme.create

      for (i <- args(0).toLong until 50000L) {
        println(s"Downloading page $i")
        retry(5) { SiteApi.page(i) } match {
          case \/-(doc) =>
            val messages = SiteApi.scrape(doc)
            val newMessages = scheme.filterNew(messages)
            println(s"Found ${newMessages.size} new messages on page $i.")
            scheme.insertAll(newMessages)
          case -\/(e) =>
            println(e.getMessage)
            e.printStackTrace()
        }

      }
    }
  }
}
