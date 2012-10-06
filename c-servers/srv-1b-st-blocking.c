/**************************************************************************
*   A single threaded blocking echo server.
*       1) Listens for TCP connections.
*       2) Waits to accepts a connection.
*       3) Reads data multiple times from the connection until it gets a 
*          full sentence (indicated by a terminating full-stop)
*       4) Converts sentence to CAPS
*       5) Writes sentence back to the socket.
*       6) Close the connection
*       7) Go to 2
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
#include <ctype.h>

#define MY_PORT     9999
#define MAXBUF      1024

void interrupt_handler(int dummy);
void uppercase(char *pc);

int main(int argc, char *argv[]) {
    signal(SIGINT, interrupt_handler);

    int sockfd;
    struct sockaddr_in listen_addr;
    char buffer[MAXBUF];

    // Create a TCP socket
    if ( (sockfd = socket(AF_INET, SOCK_STREAM, 0)) < 0 ) {
        perror("Socket");
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
        int addrlen = sizeof(client_addr);

        // Accept a connection (BLOCKING)
        clientfd = accept(sockfd, (struct sockaddr*)&client_addr, &addrlen);
        printf("%s:%d connected\n", inet_ntoa(client_addr.sin_addr), ntohs(client_addr.sin_port));

        int bytes_read = 0;
        int total_bytes_read = 0;
        int total_reads = 0;
        // Read data until client indicates end-of-sentence (BLOCKING)
        while( (bytes_read = recv(clientfd, buffer + total_bytes_read, MAXBUF, 0)) > 0) {
            // Update the bytes read counts
            total_bytes_read = total_bytes_read + bytes_read;
            total_reads++;
            printf("recv: %d of %d\n", bytes_read, total_bytes_read);

            // Check for a full-stop as it indicates end of request (cater for \n and \r\n)
            if (buffer[total_bytes_read - 2] == '.' ||
                    (buffer[total_bytes_read - 2] == '\r' && (buffer[total_bytes_read - 3] == '.'))) {
                printf("End of sentence.\n");
                break;
            }
            printf("Read more from socket...\n");
        }
        printf("Read %d in %d buffer reads.\n", total_bytes_read, total_reads);

        if (bytes_read > 0){
            printf("Processing request.\n");
            uppercase(buffer);
            printf("Sending response.\n");
            send(clientfd, buffer, total_bytes_read, 0);
        }
        else {
            printf("Client closed connection.\n");
        }
        close(clientfd);
    }
    close(sockfd);
    return 0;
}

void interrupt_handler(int dummy) {
    exit(0);
}

void uppercase(char *pc)
{
    while(*pc != '\0'){
        *pc = toupper((unsigned char)*pc);
        pc++;
    }
}
