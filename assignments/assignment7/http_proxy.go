/*****************************************************************************
 * http_proxy.go                                                                 
 * Names: Rami Farran, Zhuo Qun Song
 * NetIds: rfarran, zsong
 *****************************************************************************/

 // TODO: implement an HTTP proxy

 // compile with $ go build http_proxy.go
 // run with ./http_proxy PORT

package main

import "os"
import "fmt"
import "bufio"
import "net"
import "net/http"
// import "net/url"
import "time"

func main() {
	port := os.Args[1]

	// TODO: handle error
	ln, _ := net.Listen("tcp", ":" + port)
	for {
		// TODO: handle error
		conn, _ := ln.Accept()
		go handleConnection(conn)

	}

}

func handleConnection(conn net.Conn) {
	defer conn.Close()
	// TODO: handle connection
	req, err := http.ReadRequest(bufio.NewReader(conn))
	if err != nil {
		// TODO: HANDLE ERROR
	}
	if req.Method != http.MethodGet {
		// TODO: Handle non-GET
	}
	// Now assume that it is a well-formatted GET request.
	// If request has URL in URL field; move it to relative
	/*
	if req.URL.String() != "/" {
		req.Host = req.URL.String()
		req.URL, _ = url.Parse("/")
	}
	*/

	// Reset requestURI
	req.RequestURI = ""
	req.URL.Host = req.Host
	req.URL.Scheme = "http"
	fmt.Println(req)

	// Send request onward to server
	// 10 second timeout
	dur, _ := time.ParseDuration("10s")
	client := http.Client{nil, nil, nil, dur}
	resp, err := client.Do(req)
	fmt.Println(err)
	// TODO: Handle Error
	fmt.Println(resp)

	fmt.Println(req)
	resp.Write(conn)
	// TODO: Handle Error
}