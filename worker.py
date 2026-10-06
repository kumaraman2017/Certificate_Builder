import os
import time
from sqlalchemy.orm import Session
from PIL import Image, ImageDraw, ImageFont
import models
from database import SessionLocal

CERT_DIR = "certificates_output"
TEMPLATE_PATH = "template.png"

def create_template_if_not_exists():
    if not os.path.exists(TEMPLATE_PATH):
        img = Image.new('RGB', (1000, 700), color = (250, 250, 250))
        d = ImageDraw.Draw(img)
        # draw outer border
        d.rectangle([(20, 20), (980, 680)], outline="#C0A062", width=15)
        # draw inner border
        d.rectangle([(40, 40), (960, 660)], outline="#C0A062", width=3)
        
        # We don't write text here, we'll write it all in the worker so it can be customized.
        img.save(TEMPLATE_PATH)

def process_job(job_id: int):
    create_template_if_not_exists()
    if not os.path.exists(CERT_DIR):
        os.makedirs(CERT_DIR)
        
    db = SessionLocal()
    try:
        job = db.query(models.Job).filter(models.Job.id == job_id).first()
        if not job:
            return
        
        job.status = "processing"
        db.commit()

        certs = db.query(models.Certificate).filter(models.Certificate.job_id == job_id, models.Certificate.status == "pending").all()
        
        for cert in certs:
            try:
                # Generate certificate
                img = Image.open(TEMPLATE_PATH)
                d = ImageDraw.Draw(img)
                
                # Attempt to load nice fonts, otherwise default
                try:
                    title_font = ImageFont.truetype("arialbd.ttf", 60)
                    subtitle_font = ImageFont.truetype("arial.ttf", 30)
                    name_font = ImageFont.truetype("timesi.ttf", 70) # Times New Roman Italic
                except IOError:
                    try:
                        title_font = ImageFont.truetype("arial.ttf", 60)
                        subtitle_font = ImageFont.truetype("arial.ttf", 30)
                        name_font = ImageFont.truetype("arial.ttf", 70)
                    except IOError:
                        title_font = subtitle_font = name_font = ImageFont.load_default()
                
                # Draw standard text
                title_text = "CERTIFICATE OF COMPLETION"
                subtitle_text = "is proudly presented to"
                
                title_x = (img.width - d.textlength(title_text, font=title_font)) / 2
                d.text((title_x, 120), title_text, fill="#333333", font=title_font)
                
                sub_x = (img.width - d.textlength(subtitle_text, font=subtitle_font)) / 2
                d.text((sub_x, 230), subtitle_text, fill="#666666", font=subtitle_font)

                # Draw recipient name
                name_text = cert.recipient_name
                name_x = (img.width - d.textlength(name_text, font=name_font)) / 2
                d.text((name_x, 320), name_text, fill="#C0A062", font=name_font)
                
                # Draw signature line
                d.line([(300, 550), (700, 550)], fill="#000000", width=2)
                sig_text = "Authorized Signature"
                sig_x = (img.width - d.textlength(sig_text, font=subtitle_font)) / 2
                d.text((sig_x, 560), sig_text, fill="#000000", font=subtitle_font)
                
                output_path = os.path.join(CERT_DIR, f"cert_{cert.id}.png")
                img.save(output_path)
                
                cert.file_path = output_path
                cert.status = "generated"
            except Exception as e:
                cert.status = "failed"
                cert.error_message = str(e)
            
            db.commit()
            
        job.status = "completed"
        db.commit()
        
    finally:
        db.close()
