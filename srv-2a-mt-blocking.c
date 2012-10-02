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

int create_bind_listen_socket();
void *handle_connection(void *pClientfd);
int write_sentence(int clientfd, char buffer[], int byte_count);
int read_sentence(int clientfd, char buffer[]);
void process_sentence(char buffer[]);
void uppercase(char *pc);
void interrupt_handler(int dummy);

int main(int count, char *args[]) {
    signal(SIGINT, interrupt_handler);

    // Setup the socket listening for incoming connections.
    int sockfd = create_bind_listen_socket();
    // Thread_id struct
    pthread_t thread;

    // Accept loop
    while (1)
    {
        struct sockaddr_in client_addr;
        int addrlen = sizeof(client_addr);

        // Accept a connection (BLOCKING)
        int clientfd = accept(sockfd, (struct sockaddr*)&client_addr, &addrlen);
        printf("%s:%d connected\n", inet_ntoa(client_addr.sin_addr), ntohs(client_addr.sin_port));

        if (pthread_create(&thread, NULL, handle_connection, &clientfd) != 0) {
            fprintf(stderr, "Failed to create thread\n");
            exit(errno);
        }
    }
    close(sockfd);
    return 0;
}



int create_bind_listen_socket(){
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
    return sockfd;
}

void *handle_connection(void *pClientfd) {
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
    close(clientfd);
    return NULL;
}

int read_sentence(int clientfd, char buffer[]){
    int bytes_read = 0;
    int total_bytes_read = 0;
    int total_reads = 0;
    while((bytes_read = recv(clientfd, buffer + total_bytes_read, MAXBUF, 0)) > 0) {
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

    // If the last bytes_read was 0 the client disconnected
    if (bytes_read <= 0)
        total_bytes_read = -1;
    return total_bytes_read;
}

int write_sentence(int clientfd, char buffer[], int byte_count) {
    /* Send chunks until all bytes are written */
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
