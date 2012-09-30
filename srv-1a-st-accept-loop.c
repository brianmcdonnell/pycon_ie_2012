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

#define MY_PORT     9999
//#define MAXBUF        1024
#define MAXBUF      10

static void intHandler(int dummy) {
    //printf("Interrupt Handler!");
    exit(0);
}

int main(int Count, char *Strings[])
{
    signal(SIGINT, intHandler);

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

        /*---Echo back anything sent---*/
        int read_count = recv(clientfd, buffer, MAXBUF, 0);
        //printf("recv:%d [%s]\n", read_count, buffer);
        printf("recv:%d\n", read_count);
        send(clientfd, buffer, read_count, 0);

        /*---Close data connection---*/
        close(clientfd);
    }
    printf("Cleaning up.");
    /*---Clean up (should never get here!)---*/
    close(sockfd);
    return 0;
}

