import Swal from 'sweetalert2';
import { Form } from '../../components/Form/form';
import { useForm } from 'react-hook-form';
import isEqual from 'lodash.isequal';
import api from '../../services/api';
import { useParams, useNavigate } from 'react-router-dom';
import styles from './updatepro.module.css';
import { useState, useEffect } from 'react';

export function UpdateProduto() {
    const navigate = useNavigate();
    const { codigo } = useParams();
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [produtoData, setProdutoData] = useState(null); 

    useEffect(() => {
        async function fetchProduto() {
            setLoading(true);
            setError('');
            console.log("Código para buscar:", codigo);
            try {
                const response = await api.get(`/produto/${codigo}`);
                console.log("Resposta da busca:", response.data.produto);
                setProdutoData(response.data.produto);
            } catch (error) {
                console.error('Erro ao buscar dados do produto:', error);
                setError('Erro ao carregar os dados do produto.');
            } finally {
                setLoading(false);
            }
        }

        fetchProduto();
    }, [codigo]);

    async function handleUpdatePost(data) {
        if (isEqual(data, produtoData)) {
        Swal.fire({
            title: 'Nada alterado',
            text: 'Nenhuma modificação foi feita no produto.',
            icon: 'info',
            confirmButtonText: 'OK'
        });
        return;
    }
        try {
            console.log('handleUpdatePost foi chamada com os seguintes dados:', data);
            const response = await api.put(`/editar/${codigo}`, data);
            Swal.fire({
                title: 'Sucesso!',
                text: 'Produto atualizado com sucesso!',
                icon: 'success',
                confirmButtonText: 'OK'
            }).then(() => {
                navigate('/estoque');
            });
        } catch (error) {
            console.error('Erro ao atualizar produto:', error);
            Swal.fire({
                title: 'Erro!',
                text: 'Erro ao atualizar o produto.',
                icon: 'error',
                confirmButtonText: 'OK'
            });
        }
    }

    if (loading) {
        return <div>Carregando dados do produto...</div>;
    }

    if (error) {
        return <div>Erro: {error}</div>;
    }

    return (
        <div className={styles.container}>
            <Form
                title="Editar Produto"
                textButton="Editar"
                onAction={handleUpdatePost}
                initialValues={produtoData} 
            />
        </div>
    );
}
export default UpdateProduto;