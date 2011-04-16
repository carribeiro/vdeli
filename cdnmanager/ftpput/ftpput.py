#!/usr/bin/env python 
# -*- encoding: utf-8 -*-


from ftplib import FTP
import os, sys, getopt

def upload(srv, usr, pwd, dir_local, arquivo, dir_remoto):
    """
    Executa upload dos arquivos para o servidor FTP.

    Retorno:
        [ 0 ] Upload Concluido.
        [ 1 ] Não foi possivel estabelecer uma conexao com o servidor.
        [ 2 ] Arquivo inexistente.
        [ 3 ] Nao foi possivel autenticar-se com o usuario e senha fornecidos.
        [ 4 ] Nao foi possivel enviar arquivo desejado.

    """
    os.chdir(dir_local)

    try:
        ftp = FTP(srv,)
    except:
        return 1

    if not os.path.exists(arquivo):
        return 2

    try:
        ftp.login(usr, pwd)
    except:
        return 3

    try:
        ftp.cwd(dir_remoto)
        ftp.storbinary('STOR ' + arquivo, file(arquivo))
    except:
        return 4
     
    return 0


#ftp cliente


saidas = ["upload concluido.", 
         "[ Errno: 1 ] nao foi possivel estabelecer uma conexao com o servidor.",
         "[ Errno: 2 ] arquivo inexistente.",
         "[ Errno: 3 ] nao foi possivel autenticar-se com o usuario e senha fornecidos.",
         "[ Errno: 4 ] nao foi possivel enviar arquivo desejado."]


def main(argv):
    srv = ''
    usr = ''
    pwd = ''
    dir_local = '/tmp' 
    arquivo = ''
    dir_remoto = '/'
    try:
         opts, args = getopt.getopt(argv, "h:s:u:p:dl:a:dr", ["help", "server", "user", "passwd", "dirlocal", "arquivo", "dirremoto"])
    except getopt.GetoptError:
        print "ftpput.py -s <server> -u <user> -p <passwd>"
        sys.exit(2)
    for opt, arg in opts:
        if opt == '':
            print "ftpput.py -s <server> -u <user> -p <passwd>"
            sys.exit(1)
        elif opt in ("-s", "--server"):
            srv = arg
        elif opt in ("-u", "--user"):
            usr = arg
        elif opt in ("-p", "--passwd"):
            pwd = arg
        elif opt in ("-dl", "--dirlocal"):
            dir_local = arg
        elif opt in ("-a", "--arquivo"):
            arquivo = arg
        elif opt in ("-dr", "--dirremoto"):
            dir_remoto = arg 
    
    print "server: ", srv
    print "user: ", usr
    resultado = upload(srv, usr, pwd, dir_local, arquivo, dir_remoto) 
    print saidas[resultado]


if __name__ == "__main__":
    main(sys.argv[1:])