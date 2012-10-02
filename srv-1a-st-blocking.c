/**************************************************************************
*   A single threaded blocking echo server.
*       1) Listens for TCP connections.
*       2) Waits to accepts a connection.
*       3) Echos back the first data it receives from the connection.
*       4) Close the connection
*       5) Go to 2
**************************************************************************/
#include <stdio.h>
#include <errno.h>
#include <sys/socket.h>
#include <resolv.h>
#include <arpa/inet.h>
#include <errno.h>
#include <string.h> 
#include <stdlib.h>
#include <signal.h>

#define MY_PORT     9999
//#define MAXBUF        1024
#define MAXBUF      10

void int_handler(int dummy) {
    exit(0);
}

int main(int argc, char *argv[]) {
    signal(SIGINT, int_handler);

    int sockfd;
    struct sockaddr_in listen_addr;
    char buffer[MAXBUF];

    // Create a TCP socket
    if ( (sockfd = socket(AF_INET, SOCK_STREAM, 0)) < 0 ) {
        perror("socket");
        exit(errno);
    }

    // Allow reusable socket address
    int optval = 1;
    setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, &optval, sizeof optval);

    // Initialize address/port structure
    bzero(&listen_addr, sizeof(listen_addr));
    listen_addr.sin_family = AF_INET;
    listen_addr.sin_port = htons(MY_PORT);
    listen_addr.sin_addr.s_addr = INADDR_ANY;

    // Bind socket to a port number
    if ( bind(sockfd, (struct sockaddr*)&listen_addr, sizeof(listen_addr)) != 0 ) {
        perror("socket--bind");
        exit(errno);
    }

    // Start listening for connections (socket backlog size 20)
    if ( listen(sockfd, 20) != 0 ) {
        perror("socket--listen");
        exit(errno);
    }
    printf("Listening on %s:%d\n", inet_ntoa(listen_addr.sin_addr), ntohs(listen_addr.sin_port));

    // Accept loop
    while (1) {
        int clientfd;
        struct sockaddr_in client_addr;
        int addrlen=sizeof(client_addr);

        // Accept a connection
        clientfd = accept(sockfd, (struct sockaddr*)&client_addr, &addrlen);
        printf("%s:%d connected\n", inet_ntoa(client_addr.sin_addr), ntohs(client_addr.sin_port));

        // Read from kernel buffer into user buffer
        int read_count = recv(clientfd, buffer, MAXBUF, 0);
        printf("recv:%d bytes\n", read_count);

        // Echo back anything sent
        send(clientfd, buffer, read_count, 0);

        // Close connection
        close(clientfd);
    }

    close(sockfd);
    return 0;
}

