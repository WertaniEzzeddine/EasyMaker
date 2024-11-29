import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root',
})



export class AuthService {
  private baseUrl = 'http://127.0.0.1:8000'; // FastAPI base URL
  user = {id:0, full_name: '', email: '' };

  private booleanSubject = new BehaviorSubject<boolean>(false);
  boolean$ = this.booleanSubject.asObservable();
   // Method to update the boolean value
   setBooleanValue(value: boolean): void {
    this.booleanSubject.next(value);
  }

  // Method to get the current boolean value
  getBooleanValue(): boolean {
    return this.booleanSubject.value;
  }
  setUser(User:{id:number,full_name: string, email: string; }){
    this.user=User;
  }
  getUser(){
      return this.user;
  }
  constructor(private http: HttpClient) {}

  registerUser(userData: {full_name: string, email: string; password: string }): Observable<any> {
    return this.http.post(`${this.baseUrl}/register`, userData);
  }
  loginUser(userData: {email: string; password: string }): Observable<any> {
    return this.http.post(`${this.baseUrl}/login`, userData);
  }
}
