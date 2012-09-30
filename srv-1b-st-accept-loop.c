/**************************************************************************
*   This is a simple echo server.  This demonstrates the steps to set up
*   a streaming server.
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

void interruptHandler(int dummy);
void uppercase(char *pc);

int main(int Count, char *Strings[]) {
    signal(SIGINT, interruptHandler);

    int sockfd;
    struct sockaddr_in self;
    char buffer[MAXBUF];

    /*---Create streaming socket---*/
    if ( (sockfd = socket(AF_INET, SOCK_STREAM, 0)) < 0 )
    {
        perror("Socket");
        exit(errno);
    }

    // set SO_REUSEADDR on a socket to true (1):
    int optval = 1;
    setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, &optval, sizeof optval);

    /*---Initialize address/port structure---*/
    bzero(&self, sizeof(self));
    self.sin_family = AF_INET;
    self.sin_port = htons(MY_PORT);
    self.sin_addr.s_addr = INADDR_ANY;

    /*---Assign a port number to the socket---*/
    if ( bind(sockfd, (struct sockaddr*)&self, sizeof(self)) != 0 )
    {
        perror("socket--bind");
        exit(errno);
    }

    /*---Make it a "listening socket"---*/
    if ( listen(sockfd, 20) != 0 )
    {
        perror("socket--listen");
        exit(errno);
    }

    /*---Forever... ---*/
    while (1)
    {   int clientfd;
        struct sockaddr_in client_addr;
        int addrlen=sizeof(client_addr);

        /*---accept a connection (creating a data pipe)---*/
        clientfd = accept(sockfd, (struct sockaddr*)&client_addr, &addrlen);
        printf("%s:%d connected\n", inet_ntoa(client_addr.sin_addr), ntohs(client_addr.sin_port));

        /*--- Receive a sentence, convert to uppercase and echo it back. ---*/
        int bytes_read = 0;
        int total_bytes_read = 0;
        int total_reads = 0;
        while((bytes_read = recv(clientfd, buffer + total_bytes_read, MAXBUF, 0)) > 0) {
            // Strip out trailing LF
            if (buffer[bytes_read + total_bytes_read - 1] == '\n') {
                buffer[bytes_read + total_bytes_read - 1] = '\0';
                bytes_read--;
            }
            // Strip out trailing CR
            if (buffer[bytes_read + total_bytes_read - 1] == '\r') {
                buffer[bytes_read + total_bytes_read - 1] = '\0';
                bytes_read--;
            }

            // Update the bytes read counts
            total_bytes_read = total_bytes_read + bytes_read;
            total_reads++;
            printf("recv: %d of %d\n", bytes_read, total_bytes_read);

            // Check for a full-stop as it indicates end of request.
            if (buffer[total_bytes_read - 1] == '.'){
                printf("End of sentence.\n");
                break;
            }

            printf("Read more from socket...\n");
        }

        printf("Read %d in %d buffer reads.\n", total_bytes_read, total_reads);

        if (bytes_read > -1){
            printf("Processing request.\n");
            uppercase(buffer);
            printf("Sending response.\n");
            send(clientfd, buffer, total_bytes_read, 0);
        }
        else {
            printf("Client closed connection.\n");
        }

        /*---Close data connection---*/
        close(clientfd);
    }
    /*---Clean up (should never get here!)---*/
    close(sockfd);
    return 0;
}


void interruptHandler(int dummy) {
    exit(0);
}

void uppercase(char *pc)
{
    while(*pc != '\0'){
        *pc = toupper((unsigned char)*pc);
        pc++;
    }
}
