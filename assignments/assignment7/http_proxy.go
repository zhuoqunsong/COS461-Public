package main

import "os"
import "fmt"
import "strconv"

/*****************************************************************************
 * http_proxy.go                                                                 
 * Names: Rami Farran, Zhuo Qun Song
 * NetIds: rfarran, zsong
 *****************************************************************************/

 // TODO: implement an HTTP proxy

 // compile with $ go build http_proxy.go
 // run with ./http_proxy PORT

func main() {
	port, _ := strconv.Atoi(os.Args[1]);
	fmt.Println(port)
}