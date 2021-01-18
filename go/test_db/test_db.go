package main

import (
	"database/sql"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"

	_ "github.com/lib/pq"
)

func main() {
	connStr := "user=postgres dbname=tweetdb sslmode=verify-full"
	db, err := sql.Open("postgres", connStr)
	if err != nil {
		log.Fatal(err)
	}

	symbol := "AAPL"

	url := fmt.Sprintf("https://api.stocktwits.com/api/2/streams/symbol/%s.json", symbol)
	resp, err := http.Get(url)
	if err != nil {
		log.Fatal(err)
	}
	defer resp.Body.Close()
	body, err := ioutil.ReadAll(resp.Body)
	fmt.Println(string(body))

	_ = db

	// age := 21
	// rows, err := db.Query("SELECT name FROM users WHERE age = $1", age)
	// fmt.Println(rows)
}
