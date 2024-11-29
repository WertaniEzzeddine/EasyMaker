import { Component, OnInit } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { AuthService } from '../services/auth.service';
@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.scss']
})
export class NavbarComponent implements OnInit  {
  user:any;
  booleanValue:boolean =false;
  constructor(private authService:AuthService){};

  logout(){
    this.booleanValue=false;

  }
  ngOnInit(): void {
    // Subscribe to the boolean value
    this.authService.boolean$.subscribe(value => {
      this.booleanValue = value;
    });
  }
}
