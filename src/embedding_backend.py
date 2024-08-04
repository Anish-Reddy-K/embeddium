# embedding_backend.py

import torch
from sentence_transformers import SentenceTransformer
import os
import json
import pandas as pd
import numpy as np
import h5py
import faiss
from tqdm import tqdm
import time
import psutil
import chardet
from PyQt5.QtCore import QObject, pyqtSignal

class EmbeddingBackend(QObject):
    progress_updated = pyqtSignal(dict)
    embedding_completed = pyqtSignal(str, dict)
    error_occurred = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.supported_input_formats = ['.txt', '.csv', '.json', '.xlsx']
        self.supported_output_formats = ['pt', 'npy', 'hdf5', 'faiss']
        self.cancel_flag = False

    def cancel_embedding(self):
        self.cancel_flag = True

    def detect_encoding(self, file_path):
        with open(file_path, 'rb') as file:
            raw_data = file.read()
        return chardet.detect(raw_data)['encoding']

    def read_file(self, file_path):
        _, file_extension = os.path.splitext(file_path)
        
        if file_extension not in self.supported_input_formats:
            raise ValueError(f"Unsupported file format: {file_extension}")
        
        if file_extension == '.txt':
            with open(file_path, 'r', encoding='utf-8') as file:
                return [line.strip() for line in file if line.strip()]
        
        elif file_extension == '.csv':
            encoding = self.detect_encoding(file_path)
            df = pd.read_csv(file_path, encoding=encoding, header=None)
            return [' '.join(row.astype(str)) for _, row in df.iterrows()]
        
        elif file_extension == '.json':
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                return [json.dumps(item) for item in data]
        
        elif file_extension == '.xlsx':
            df = pd.read_excel(file_path, header=None)
            return [' '.join(row.astype(str)) for _, row in df.iterrows()]

    def save_embeddings(self, embeddings, output_path, output_format):
        if output_format == 'pt':
            torch.save(embeddings, output_path)
        elif output_format == 'npy':
            np.save(output_path, embeddings.numpy())
        elif output_format == 'hdf5':
            with h5py.File(output_path, 'w') as f:
                f.create_dataset('embeddings', data=embeddings.numpy())
        elif output_format == 'faiss':
            index = faiss.IndexFlatL2(embeddings.shape[1])
            index.add(embeddings.numpy())
            faiss.write_index(index, output_path)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")

    def embed_file(self, input_file_path, output_directory, model_name, output_name, output_format, batch_size):
        self.cancel_flag = False
        output_format = output_format.lstrip('.')
        if output_format not in self.supported_output_formats:
            raise ValueError(f"Unsupported output format: {output_format}")

        start_time = time.time()
        process = psutil.Process(os.getpid())
        peak_memory_usage = 0
        
        try:
            model = SentenceTransformer(model_name)
            texts = self.read_file(input_file_path)
            total_items = len(texts)

            embeddings = []
            error_count = 0
            
            for i in range(0, total_items, batch_size):
                if self.cancel_flag:
                    raise InterruptedError("Embedding process was cancelled")

                batch = texts[i:i+batch_size]
                try:
                    batch_embeddings = model.encode(batch, convert_to_tensor=True)
                    embeddings.extend(batch_embeddings)
                except Exception as e:
                    error_count += len(batch)
                    self.error_occurred.emit(f"Error embedding batch {i//batch_size + 1}: {str(e)}")
                
                items_processed = min(i + batch_size, total_items)
                progress = items_processed / total_items * 100
                elapsed_time = time.time() - start_time
                speed = items_processed / elapsed_time if elapsed_time > 0 else 0
                eta = (total_items - items_processed) / speed if speed > 0 else 0
                
                current_memory_usage = process.memory_info().rss / 1024**2
                peak_memory_usage = max(peak_memory_usage, current_memory_usage)
                
                stats = {
                    "progress": progress,
                    "items_processed": items_processed,
                    "total_items": total_items,
                    "speed": speed,
                    "eta": eta,
                    "error_count": error_count,
                    "memory_usage": current_memory_usage,
                    "embedding_dim": model.get_sentence_embedding_dimension(),
                    "model_name": model_name,
                    "output_size": len(embeddings) * model.get_sentence_embedding_dimension() * 4 / 1024**2
                }
                
                self.progress_updated.emit(stats)

            if self.cancel_flag:
                raise InterruptedError("Embedding process was cancelled")

            embeddings_tensor = torch.stack(embeddings)

            output_file_path = os.path.join(output_directory, f"{output_name}.{output_format}")
            self.save_embeddings(embeddings_tensor, output_file_path, output_format)

            total_time = time.time() - start_time
            final_stats = {
                "progress": 100,
                "items_processed": total_items,
                "total_items": total_items,
                "speed": total_items / total_time,
                "eta": 0,
                "error_count": error_count,
                "memory_usage": peak_memory_usage,
                "embedding_dim": model.get_sentence_embedding_dimension(),
                "model_name": model_name,
                "output_size": os.path.getsize(output_file_path) / 1024**2,
                "total_time": total_time,
                "output_file": output_file_path
            }
            self.embedding_completed.emit(output_file_path, final_stats)

        except InterruptedError as e:
            self.error_occurred.emit(str(e))
        except Exception as e:
            self.error_occurred.emit(f"An error occurred: {str(e)}")