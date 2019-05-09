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
// import "strconv"
import "net"
import "io/ioutil"

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
	fmt.Println("connected")
	// TODO: handle connection
	in, _ := ioutil.ReadAll(conn)
	inStr := string(in)
	fmt.Println(inStr)
}