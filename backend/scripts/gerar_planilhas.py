"""Gera planilhas fictícias sem precisar do banco (útil antes do seed)."""

from datetime import date, timedelta
from pathlib import Path

import pandas as pd

DESTINO = Path(__file__).resolve().parents[2] / "dados_demo"
TIPOS = ["seguro", "consorcio", "financiamento", "plano_saude", "investimento"]


def main() -> None:
    DESTINO.mkdir(exist_ok=True)
    hoje = date.today()
    linhas = []
    for i in range(1, 41):
        linhas.append(
            {
                "codigo": f"IMP-{i:04d}",
                "documento_cliente": f"{20000000000 + i:011d}",
                "nome_cliente": f"Cliente Importacao {i}",
                "tipo": TIPOS[i % len(TIPOS)] if i % 11 else "",
                "valor": "" if i % 13 == 0 else round(2500 + i * 110.5, 2),
                "data_operacao": (hoje - timedelta(days=20 + i)).isoformat(),
                "data_vencimento": (
                    hoje - timedelta(days=3) if i % 7 == 0 else (hoje + timedelta(days=i)).isoformat()
                ),
                "status_operacao": "aberta",
                "observacao": "linha de teste de importação",
            }
        )
    df = pd.DataFrame(linhas)
    df.to_csv(DESTINO / "operacoes_demo.csv", index=False)
    df.to_excel(DESTINO / "operacoes_demo.xlsx", index=False)
    df.head(12).to_excel(DESTINO / "operacoes_amostra.xlsx", index=False)
    print(f"Planilhas gravadas em {DESTINO}")


if __name__ == "__main__":
    main()
