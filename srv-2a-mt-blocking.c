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
#include <unistd.h>
#include <pthread.h>

#define MY_PORT     9999
#define MAXBUF      1024

int create_bind_listen_socket(int port);
void *handle_connection(void *pClientfd);
int write_sentence(int clientfd, char buffer[], int byte_count);
int read_sentence(int clientfd, char buffer[]);
void process_sentence(char buffer[]);
void uppercase(char *pc);
void interrupt_handler(int dummy);

int main(int count, char *args[]) {
    signal(SIGINT, interrupt_handler);

    // Setup the socket listening for incoming connections.
    int sockfd = create_bind_listen_socket(MY_PORT);

    // Thread_id struct
    pthread_t thread;
    // Loop forever
    while (1)
    {
        struct sockaddr_in client_addr;
        int addrlen = sizeof(client_addr);

        /*--- accept a connection (when one arrives) ---*/
        int clientfd = accept(sockfd, (struct sockaddr*)&client_addr, &addrlen);
        printf("%s:%d connected\n", inet_ntoa(client_addr.sin_addr), ntohs(client_addr.sin_port));

        if (pthread_create(&thread, NULL, handle_connection, &clientfd) != 0) {
            fprintf(stderr, "Failed to create thread\n");
        }
        //handle_connection(clientfd);
    }
    /*---Clean up (should never get here!)---*/
    close(sockfd);
    return 0;
}

int create_bind_listen_socket(int port){
    int sockfd;
    struct sockaddr_in self;

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

    return sockfd;
}

void *handle_connection(void *pClientfd) {
    /*--- Receive a sentence, convert to uppercase and echo it back. ---*/
    int clientfd = *(int*)pClientfd;
        
    char buffer[MAXBUF];

    int bytes_read = read_sentence(clientfd, buffer);

    if (bytes_read > -1){
        printf("Processing request.\n");
        process_sentence(buffer);
        printf("Sending response.\n");
        write_sentence(clientfd, buffer, bytes_read);
    }
    else {
        printf("Client closed connection.\n");
    }

    /*---Close data connection---*/
    close(clientfd);
    return NULL;
}

int read_sentence(int clientfd, char buffer[]){
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

    // If the last bytes read was -1 the client disconnected
    if (bytes_read <= 0)
        total_bytes_read = -1;
    return total_bytes_read;
}

int write_sentence(int clientfd, char buffer[], int byte_count) {
    /* Send the chunk */
    int i;
    int nwritten;
    for (i = 0; i < byte_count; i += nwritten) {
        nwritten = send(clientfd, buffer + i, byte_count, 0);
        if (nwritten < 0) 
            perror("write failed");
    }
}

void process_sentence(char buffer[]) {
    //usleep(2000*1000);
    uppercase(buffer);
}

void uppercase(char *pc)
{
    while(*pc != '\0'){
        *pc = toupper((unsigned char)*pc);
        pc++;
    }
}

void interrupt_handler(int dummy) {
    exit(0);
}
