/*****************************************************************************
 * http_proxy_DNS.go                                                                 
 * Names: Rami Farran, Zhuo Qun Song
 * NetIds: rfarran, zsong
 *****************************************************************************/

package main

import "os"
import "fmt"
import "bufio"
import "net"
import "net/http"
import "time"
import "golang.org/x/net/html"

func main() {
	if len(os.Args) != 2 {
		fmt.Println("Usage: ./http_proxy PORT")
		return
	}
	port := os.Args[1]

	// TODO: handle error
	ln, err := net.Listen("tcp", ":" + port)
	if err != nil {
		fmt.Println("Unable to create server at port " + port)
		return
	}
	for {
		conn, err := ln.Accept()
		if err != nil {
			fmt.Println("Error in establishing connection")
		} else {
			go handleConnection(conn)			
		}
	}
}

func handleConnection(conn net.Conn) {
	defer closeConnection(conn)
	// TODO: handle connection
	req, err := http.ReadRequest(bufio.NewReader(conn))
	if err != nil {
		write500(conn)
		return
	}
	if req.Method != http.MethodGet {
		write500(conn)
		return
	}
	// Now assume that it is a well-formatted GET request.

	// Reset requestURI
	req.RequestURI = ""
	req.URL.Host = req.Host
	req.URL.Scheme = "http"
	// fmt.Println(req)

	// Send request onward to server
	// 10 second timeout
	dur, _ := time.ParseDuration("10s")
	client := http.Client{nil, nil, nil, dur}
	resp, err := client.Do(req)
	if err != nil {
		write500(conn)
		return
	}

	resp2, _ := client.Do(req)
	// copy for DNS caching


	// fmt.Println(resp)
	err = resp.Write(conn)
	if err != nil {
		fmt.Println("Error in writing to existing connection")
		return
	}

	// intercept response
	foundLinks := make([]string, 0)
	doc, err := html.Parse(resp2.Body)
	if err != nil {
		fmt.Println("error in parsing html ")
		fmt.Println(err)
		return
	}
	var f func(*html.Node)
	f = func(n *html.Node) {
		if n.Type == html.ElementNode && n.Data == "a" {
			for _, a := range n.Attr {
				if a.Key == "href" {
					foundLinks = append(foundLinks, a.Val)
					break
				}
			}
		}
		for c := n.FirstChild; c != nil; c = c.NextSibling {
			f(c)
		}
	}
	f(doc)

	// for each link in foundLinks, issue DNS queries
	for _, link := range foundLinks {
		go prefetchLink(link)
	}
}

func prefetchLink(link string) {
	_, err := net.LookupHost(link)
	if err == nil {
		return
	}
}

func write500(conn net.Conn) {
	_, err := conn.Write([]byte("HTTP/1.1 500 Internal Error\r\n"))
	if err != nil {
		fmt.Println("Error in writing to existing connection")
		return
	}
}

func closeConnection(conn net.Conn) {
	err := conn.Close()
	if err != nil {
		fmt.Println("Error in closing connection")
		return
	}
}