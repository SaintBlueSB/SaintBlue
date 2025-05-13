import styles from './formmm.module.css';
import { useForm } from "react-hook-form";
import { useNavigate } from 'react-router-dom';
import { useEffect } from 'react'; // Importe useEffect

export function Form({title, textButton, onAction, initialValues}) { // Receba initialValues
    const {register, handleSubmit, setValue} = useForm(); // Obtenha setValue

    const navigate = useNavigate();

    useEffect(() => {
        if (initialValues) {
            setValue('codigo', initialValues.codigo);
            setValue('condicao', initialValues.condicao);
            setValue('cor', initialValues.cor);
            setValue('marca', initialValues.marca);
            setValue('peso', initialValues.peso);
            setValue('preco', initialValues.preco);
            setValue('quantidade', initialValues.quantidade);
            setValue('produto', initialValues.produto);
            setValue('observacoes', initialValues.observacoes);
        }
    }, [initialValues, setValue]); 
    return (
        <div className={styles.formmm}>
            <form onSubmit={handleSubmit(onAction)}>
                <h2>{title}</h2>
                <div className={styles.inputf}>
                    <label htmlFor="codigo">Código:</label>
                    <input id="codigo" {...register('codigo')} required />
                </div>
                <div className={styles.inputf}>
                    <label htmlFor="condicao">Condição:</label>
                    <input id="condicao" {...register('condicao')} required />
                </div>
                <div className={styles.inputf}>
                    <label htmlFor="cor">Cor:</label>
                    <input id="cor" {...register('cor')} required />
                </div>
                <div className={styles.inputf}>
                    <label htmlFor="marca">Marca:</label>
                    <input id="marca" {...register('marca')} required />
                </div>
                <div className={styles.inputf}>
                    <label htmlFor="peso">Peso:</label>
                    <input id="peso" {...register('peso')} required />
                </div>
                <div className={styles.inputf}>
                    <label htmlFor="preco">Preço:</label>
                    <input id="preco" {...register('preco')} required />
                </div>
                <div className={styles.inputf}>
                    <label htmlFor="quantidade">Quantidade:</label>
                    <input id="quantidade" {...register('quantidade')} required />
                </div>
                <div className={styles.inputf}>
                    <label htmlFor="produto">Produto:</label>
                    <input id="produto" {...register('produto')} required />
                </div>
                <div className={styles.inputobs}>
                    <label htmlFor="observacoes">Observações:</label>
                    <textarea id="observacoes" {...register('observacoes')} required></textarea>
                </div>
                <div className={styles.button}>
                    <button type='submit'>{textButton}</button>
                    <button type="button" onClick={() => navigate('/estoque')}>Cancelar</button>
                </div>
            </form>
        </div>
    )
}