import { Link, useNavigate } from "react-router-dom";
import React, { useState, useEffect } from "react";
import "./login.css";
import Swal from "sweetalert2";


function Login() {
    const [isActive, setIsActive] = useState(false);
    const navigate = useNavigate();

    const handleRegisterClick = () => setIsActive(true);
    const handleLoginClick = () => setIsActive(false);

    useEffect(() => {
        document.body.classList.add("login-page");
        return () => document.body.classList.remove("login-page");
    }, []);

    // Função para lidar com o envio do formulário de cadastro
    const handleRegisterSubmit = async (e) => {
        e.preventDefault();
    
        const nome = e.target.nome.value;
        const sobrenome = e.target.sobrenome.value;
        const email = e.target.email.value;
        const telefone = e.target.telefone.value;
        const senha = e.target.senha.value;
        const confirmSenha = e.target.confirmarsenha.value;
    
        if (senha !== confirmSenha) {
            Swal.fire({
                icon: "error",
                title: "Erro",
                text: "As senhas não coincidem!",
                confirmButtonColor: "#3085d6",
            });
            return;
        }
    
        try {
            const response = await fetch("http://192.168.1.145:5001/new_user", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    nome,
                    sobrenome,
                    email,
                    numero: telefone,
                    senha,
                }),
            });
    
            if (response.ok) {
                Swal.fire({
                    icon: "success",
                    title: "Sucesso!",
                    text: "Conta criada com sucesso!",
                    confirmButtonColor: "#3085d6",
                }).then(() => {
                    setIsActive(false); // Alterna para a tela de login
                });
            } else {
                const errorData = await response.json();
                Swal.fire({
                    icon: "error",
                    title: "Erro ao criar conta",
                    text: errorData.error,
                    confirmButtonColor: "#d33",
                });
            }
        } catch (error) {
            Swal.fire({
                icon: "error",
                title: "Erro de conexão",
                text: error.message,
                confirmButtonColor: "#d33",
            });
        }
    };

    // Função para lidar com o envio do formulário de login
    const handleLoginSubmit = async (e) => {
        e.preventDefault();
    
        const email = e.target.email.value;
        const senha = e.target.senha.value;
    
        try {
            const response = await fetch("http://192.168.1.145:5001/login", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ email, senha }),
            });
    
            if (response.ok) {
                const data = await response.json();
                console.log("Token:", data.token); // Você pode salvar o token no localStorage ou em outro lugar
                localStorage.setItem("token", data.token);
                navigate("/inicio"); // Redireciona diretamente para a página inicial
            } else {
                const errorData = await response.json();
                Swal.fire({
                    icon: "error",
                    title: "Erro ao fazer login",
                    text: errorData.error,
                    confirmButtonColor: "#d33",
                });
            }
        } catch (error) {
            Swal.fire({
                icon: "error",
                title: "Erro de conexão",
                text: error.message,
                confirmButtonColor: "#d33",
            });
        }
    };
    

    return (
        <div className="login-container">
            <div className={`container ${isActive ? "active" : ""}`} id="container">
                <div className="form-container cadastro">
                    <form onSubmit={handleRegisterSubmit}>
                        <h1>Cadastre-se</h1>
                        <input
                            type="text"
                            name="nome"
                            placeholder="Nome"
                            required
                            minLength="4"
                            maxLength="15"
                        />
                        <input
                            type="text"
                            name="sobrenome"
                            placeholder="Sobrenome"
                            required
                            minLength="4"
                            maxLength="15"
                        />
                        <input
                            type="email"
                            name="email"
                            placeholder="E-mail"
                            required
                            minLength="3"
                            maxLength="30"
                        />
                        <input
                            type="tel"
                            name="telefone"
                            placeholder="Número"
                            required
                        />
                        <input
                            type="password"
                            name="senha"
                            placeholder="Senha"
                            required
                            minLength="8"
                            maxLength="20"
                        />
                        <input
                            type="password"
                            name="confirmarsenha"
                            placeholder="Confirme sua senha"
                            required
                            minLength="8"
                            maxLength="20"
                        />
                        <button type="submit">Criar conta</button>
                    </form>
                </div>

                <div className="form-container llogin">
                    <form onSubmit={handleLoginSubmit}>
                        <h1>Login</h1>
                        <input type="email" name="email" placeholder="E-mail" required />
                        <input
                            type="password"
                            name="senha"
                            placeholder="Senha"
                            required
                        />
                        <button type="submit">Entrar</button>
                    </form>
                </div>

                <div className="painel-container">
                    <div className="painel">
                        <div className="painel2 painel-esquerda">
                            <div className="logo1">
                            <img src="/s.png" alt="Logo SaintBlue" />
                            </div>
                            <h1>Bem-vindo(a)</h1>
                            <p>Já possui uma conta?</p>
                            <button className="hidden" onClick={handleLoginClick}>
                                Fazer login
                            </button>
                            <Link to="/">
                                <button className="hidden2">Home</button>
                            </Link>
                        </div>
                        <div className="painel2 painel-direita">
                            <div className="logo2">
                            <img src="/s.png" alt="Logo SaintBlue" />
                            </div>
                            <h1>Bem-vindo(a)</h1>
                            <p>Não possui uma conta?</p>
                            <button className="hidden" onClick={handleRegisterClick}>
                                Criar conta
                            </button>
                            <Link to="/">
                                <button className="hidden2">Home</button>
                            </Link>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Login;